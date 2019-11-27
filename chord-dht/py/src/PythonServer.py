#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import glob
import sys
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('/home/yaoliu/src_code/local/lib/lib/python2.7/site-packages')[0])

from chord import FileStore
from chord.ttypes import SystemException, RFileMetadata, RFile, NodeID

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import socket # ip address
import hashlib # SHA-256
import os # creating directories
import shutil # deleting a directory and its contents

'''
Helper methods
'''

def getID(ip, port):
    return hashlib.sha256( (ip + ':' + str(port)).encode('utf-8') ).hexdigest()

def getHash(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def retException(msg):
    se = SystemException()
    se.message = msg
    print('%s' % msg)
    return se

nodeID = None

class FileStoreHandler:

    # Finger Table
    ft = None # array of NodeID objects

    # RFiles on this server
    serverDir = None
    files = {} # filename -> RFile 

    # Predecessor NodeID
    pred = None

    def __init__(self):
        self.log = {}

        # Create a directory for the files that are stored on this server
    
        # Check if the main files directory exists
        if not os.path.isdir('files'):
            raise retException('Files directory does not exist.')

        self.serverDir = os.getcwd() + '/' + 'files/' + str(port)
        if not os.path.isdir(self.serverDir):
            try:
                os.mkdir(self.serverDir)
            except:
                raise retException('Failed to create ' + self.serverDir + ' directory.')
        
        #print('%i: Server directory: %s, isDirectory=%s' % (nodeID.port, self.serverDir, os.path.isdir(self.serverDir)))
 
    # If key is between n1 and n2, return true 
    def inRange(self, key, node1, node2): # n1 and n2 are ids (hashes in hex)
        k = int(key, 16) # convert from hex to integer
        n1 = int(node1, 16)
        n2 = int(node2, 16)
        mod = pow(2, 256)
        #print('k=%i, n1=%i, n2=%i' % (k, n1, n2))       
 
        # Range goes over zero wrap-around
        if n1 > n2:
            print('%i: inRange() n1 and n2 wrap around zero' % (nodeID.port))
            d = mod - n1 # difference to zero
            n1 = 0
            k = (k+d) % mod
            n2 = (n2+d) % mod

        if n1 > n2:
            print('%i: Failed range adjustment' % nodeID.port)
            return False

        if k >= n1 and k <= n2:
            return True
        else:
            return False
   
    '''
    Methods defined in chord.thrift (IDL file)
    '''

    def writeFile(self, rFile):
        if not os.path.isdir(self.serverDir):
            raise retException("Directory " + self.serverDir + " does not exist")
        
        print('%i: writeFile()' % port)
        #print('rFile', rFile)
        filename = rFile.meta.filename
        
        # Check if this server is the file's successor
        h = getHash(filename)
        s = self.findSucc(h)
        if s.id != nodeID.id:
            print('%i: The successor of %s should be %i, not %i' % (nodeID.port, filename, s.port, nodeID.port))
            raise retException("The successor of " + filename + " is not node " + str(nodeID.port) + ". Write failed.")

        # Add or update this file to the RFiles dictionary
        if filename not in self.files.keys():
            print('%i: %s was not found. Creating.' % (nodeID.port, rFile.meta.filename))
            self.files[filename] = RFile()
            f = self.files[filename]
            f.content = rFile.content
            f.meta = RFileMetadata()
            f.meta.filename = filename
            f.meta.version = 0
            f.meta.contentHash = getHash(rFile.content)
        else:
            f = self.files[filename]
            f.content = rFile.content # overwrite content
            f.meta.version += 1
            f.meta.contentHash = getHash(rFile.content) # update content hash

       
        path = self.serverDir + '/' + filename
        print('path=%s' % path)
        try:
            f = open(path, 'w')
            f.write(rFile.content)
            f.close()
        except:
            raise retException("Failed to open "  + filename)
        
        print('%i: Wrote to file %s' % (nodeID.port, filename))

    def readFile(self, filename): # returns an RFile
        print('%i: readFile()' % port)

        h = getHash(filename)
        if nodeID.id != self.findSucc(h).id:
            raise retException("The successor of " + filename + " is not node " + str(nodeID.port) + ". Read failed.")
        
        if filename not in self.files.keys():
            raise retException(filename + " does not exist")

        return self.files[filename]

    def setFingertable(self, node_list):
        print('%i: setFingerTable()' % port)
        if node_list is None:
            raise retException('Server at port ' + str(nodeID.port) + ' did not receive a Finger Table')
        #print('%i: Finger Table' % nodeID.port)
        #for n in node_list:
        #    print(n)
        self.ft = node_list[:]
  
    def findSucc(self, key): # returns a NodeID
        print('%i: findSucc()' % port)
        if self.inRange(key, nodeID.id, self.getNodeSucc().id):
            return self.getNodeSucc() 
        else:
            # Hop to the closest preceding node
            p = self.findPred(key)
            if p.port == nodeID.port:
                print('%i: Got node %i as successor' % (nodeID.port, p.port))
                return nodeID           
 
            # Make socket connection to the predecessor
            transport = TSocket.TSocket(p.ip, p.port)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = FileStore.Client(protocol)
            
            # Connect!
            print('%i: Creating connection with port %i' % (nodeID.port, p.port))
            transport.open()
            n = client.findSucc(key)
            transport.close()
            print('%i: Got node %i as successor' % (nodeID.port, n.port))
        
            return n

    def findPred(self, key): # returns a NodeID
        print('%i: findPred()' % port)
        if self.ft is None:
            raise retException("A Finger Table for server at port " + str(nodeID.port) + " was not found.")

        if self.pred is not None:
            return self.pred

        for i in range(len(self.ft)-1, -1, -1): # len(Finger Table) down to 0
            n = self.ft[i]
            print('%i: findPred() i=%i, port=%i' % (nodeID.port, i, n.port))
            if self.inRange(n.id, nodeID.id, key):
                print("findPred() Returning node at port %i" % n.port)
                self.pred = n
                return n
      
        print('%i: Returning this node as predecessor... Should not happen...' % nodeID.port) 
        return nodeID
 
    def getNodeSucc(self): # returns a NodeID
        print('%i: getNodeSucc()' % port)
        if self.ft is None:
            raise retException("A Finger Table for server at port " + str(nodeID.port) + " was not found.")
       
        print('%i: The successor of %i is %i' % (nodeID.port, nodeID.port, self.ft[0].port)) 
        return self.ft[0]

    # Destructor
    def __del__(self):
        # Remove directory
        try:
            shutil.rmtree(self.serverDir)
        except:
            print('Failed to remove %s' % self.serverDir)
        
        print('%i: Node at %s:%i leaving' % (nodeID.port, nodeID.ip, nodeID.port))

if __name__ == '__main__':
    port = int(sys.argv[1])
    ip = socket.gethostbyname(socket.gethostname())
    nodeID = NodeID()
    nodeID.id = getID(ip, port)
    nodeID.ip = ip
    nodeID.port = port

    handler = FileStoreHandler()
    processor = FileStore.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)

    print('%i: Starting the server: %s %i' % (port, ip, port))
    server.serve()
    print('%i: done.' % port)
