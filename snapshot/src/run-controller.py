#!/usr/bin/env python

import sys, time, socket

from Branch import Branch
from Controller import Controller

sys.path.append('/home/yaoliu/src_code/protobuf-3.7.0/python')

import bank_pb2

# Main procedure
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<Total amount of money in distributed bank> <branches.txt>")
    sys.exit()

branch_file = 'branches.txt' # default
if len(sys.argv) == 3:
    branch_file = sys.argv[2]

# Create a Controller object ; parses branches.txt file
cont = Controller(sys.argv[1], branch_file)

# Create a TCP connection with every branch
#cont.connectToAllBranches()

num_snapshots = 5
for i in range(0, num_snapshots):
    # Send InitBranch message to all branches
    cont.sendInitBranchToAll()
    
    # Start listening for snapshot messages
    #for port in cont.branches.keys():
    #    b = cont.branches[port]
    #    message = b.sock.recv(4096)
    #    bm = bank_pb2.BranchMessage()
    #    bm.ParseFromString(message)
    #    print('received', bm)
    
    # Send InitSnapshot message to a random branch
    cont.sendInitSnapshot()
    
    time.sleep(1)
    
    # Send RetreiveSnapshot to all branches and listen at ports
    cont.sendRetrieveSnapshotToAll()
    
    # Get and save snapshot messages
    snapshots = cont.getSnapshots()
    cont.checkSnapshots(snapshots)
#print('snapshots', snapshots)

# Close connections with all branches
#cont.closeAllConnections()
