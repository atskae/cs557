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

from keyval import KeyValStore # Import the KeyValStore service defined in keyval.thrift
from keyval.ttypes import SystemException, NodeID, ConstMethod, ConstLevel # Import the data types defined in keyval.thrift

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import socket

# Server Node
class KeyValStoreHandler:
    
    ip = None
    port = None
    node_list = None # list of NodeID objects; information about all of the replica nodes

    constMethod = None # either READ_REPAIR or HINTED_HANDOFF

    def __init__(self, ip, port):
        self.log = {}
        
        self.ip = ip
        self.port = port
    
    def retException(self, msg):
        se = SystemException()
        se.message = msg
        print('%s' % msg)
        return se
    
    def connect(ip, port):
        
        # Make socket
        transport = TSocket.TSocket(ip, port)
    
        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)
    
        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
        # Create a client to use the protocol encoder
        client = KeyValStore.Client(protocol)
    
        # Connect!
        transport.open()
    
        return (transport, client)

    '''
    Methods defined in keyval.thrift (IDL file)
    '''
    
    def initServer(self, node_list, constMethod): # node_list contains information about all the replica nodes
        print('%i: initServer()' % self.port)
        if node_list is None:
            raise retException(str(self.port) + ': Received empty node_list')
        
        print('%i: Obtained node_list:' % port)
        print('Consistency Method', constMethod)

        for n in node_list:
            print(n)
        
        self.node_list = node_list[:]
        self.constMethod = constMethod

    def get(self, key, constLevel): # key = 8-bit integer ; constLevel = ONE/QUORUM ; returns string
        if key is None:
            raise retException(str(self.port) + ': Received empty key')

        print('%i: get() key=%i' % (self.port, key))
        print('Consistency level', constLevel)

    def put(self, key, val, constLevel):
        print('%i: put() key=%i, val=%s' % (self.port, key, val))
        print('Consistency level', constLevel)

    def __del__(self):
        print('%i: Closing server' % self.port)

if __name__ == '__main__':
   
    if len(sys.argv) != 2:
        print('Server.py <port #>')
        sys.exit()

    port = int(sys.argv[1])
    ip = socket.gethostbyname(socket.gethostname())
    
    handler = KeyValStoreHandler(ip, port)
    processor = KeyValStore.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)

    print('%i: Starting the server...' % port)
    server.serve()
    print('%i: done.' % port)
