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

from keyval import KeyValStore # Import the KeyValStore service defined in keyval.thrift
from keyval.ttypes import SystemException, NodeID, ConstMethod, ConstLevel # Import the data types defined in keyval.thrift

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Returns tuple (transport, client)
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

def main():

    if len(sys.argv) != 3:
        print('Client.py <ip> <port>')
        sys.exit()
   
    ip = sys.argv[1]
    port = int(sys.argv[2]) 
    (transport, client) = connect(ip, port)
    print('%i: client starting...' % port)
 
    '''
    Call KeyValStore methods on Server.py
    '''

    try:
        client.get(5, ConstLevel.ONE)
    except:
        pass
    
    client.put(25, 'Pikachu', ConstLevel.QUORUM)

    print('%i: client closing connection' % port)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx.message)
