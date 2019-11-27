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

import sys, glob, socket, random, subprocess, time
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

    # Consistency method (READ_REPAIR or HINTED_HANDOFF)
    constMethod = ConstMethod.READ_REPAIR

    # Start 4 replica nodes at different ports
    ip = socket.gethostbyname(socket.gethostname())
    node_list = [] # NodeID objects
    running = [] # nodes that started
    for i in range(0, 4):
        port = random.randint(50000, 65535)
        n = NodeID()
        n.id = ip + ':' + str(port)
        n.ip = ip
        n.port = port 
        node_list.append(n)
       
        args = ['./server.sh', str(port)]
        try:
            running.append(subprocess.Popen(args))
        except:
            print('Failed to launch', args)

    # Wait until all nodes are listening
    time.sleep(1)

    # Send node_list to each replica node
    for n in node_list:
        (transport, client) = connect(n.ip, n.port)
        client.initServer(node_list, constMethod)
        transport.close()

    print('All replicas initialized.')
    while True:
        pass

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx.message)
