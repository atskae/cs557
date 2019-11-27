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

import sys
import glob
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('/home/yaoliu/src_code/local/lib/lib/python2.7/site-packages')[0])

from chord import FileStore
from chord.ttypes import SystemException, RFileMetadata, RFile, NodeID

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import hashlib # SHA-256

def getID(ip, port):
    return hashlib.sha256( (ip + ':' + str(port)).encode('utf-8') ).hexdigest()

def getHash(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

# Returns tuple (transport, client)
def openConnection(ip, port):
    
    # Make socket
    transport = TSocket.TSocket(ip, port)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = FileStore.Client(protocol)

    # Connect!
    transport.open()

    return (transport, client)

def main():
   
    ip = sys.argv[1]
    port = int(sys.argv[2]) 
    (transport, client) = openConnection(ip, port)
  
    '''
    Call FileStore methods on PythonServer.py
    '''

    h = getID(ip, port)
    p = client.findPred(h)
    print('The predecessor of %i is %i' % (port, p.port))
   
    f = RFile()
    f.content = "Tomato! Wahoo."
    f.meta = RFileMetadata()
    f.meta.filename = "tomato.txt"

    s = client.findSucc(getHash(f.meta.filename))
    print('The successor of %s is %i' % (f.meta.filename, s.port))

    if s.port != port:
        #print('Will write to incorrect server...')
        #try:
        #client.writeFile(f)
        #except SystemException as se:
        #    print('Wrong server: %s' % se.message)
        #    return
        transport.close()
        print('Connecting with correct server at port %i' % s.port)
        (transport, client) = openConnection(ip, s.port)

    # Attempt to read non-existent file
    #client.readFile('asparagus.txt')

    client.writeFile(f)
    r = client.readFile(f.meta.filename)
    print('contents of %s is %s' % (f.meta.filename, f.content))
 
    #client.readFile('Hello')

    #client.setFingertable(None)
  
    #client.findSucc('key') 

    #client.findPred('key')
        
    #n = client.getNodeSucc()
    #print('client: getNodeSucc() returned', n)
    
    #sum_ = client.add(1, 1)
    #print('1+1=%d' % sum_)

    #work = Work()

    #work.op = Operation.DIVIDE
    #work.num1 = 1
    #work.num2 = 0

    #try:
    #    quotient = client.calculate(1, work)
    #    print('Whoa? You know how to divide by zero?')
    #    print('FYI the answer is %d' % quotient)
    #except InvalidOperation as e:
    #    print('InvalidOperation: %r' % e)

    #work.op = Operation.SUBTRACT
    #work.num1 = 15
    #work.num2 = 10

    #diff = client.calculate(1, work)
    #print('15-10=%d' % diff)

    #log = client.getStruct(1)
    #print('Check log: %s' % log.value)

    # Close!
    print('Client closing connection')
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx.message)
