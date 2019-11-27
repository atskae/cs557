import sys, socket
from random import randint

from Branch import Branch

sys.path.append('/home/yaoliu/src_code/protobuf-3.7.0/python')
import bank_pb2

class Controller():
    name = 'controller'
    balance = 0
    branches = {} # port -> Branch object
    snapshot_id = 1 # increments everytime InitSnapshot message is sent
    send_snapshot_id = 1

    def __init__(self, balance, branch_file):
       
        self.balance = int(balance)
        
        # Parse branches.txt
        try:
            with open(branch_file, "rb") as f:
                for line in f:
                    name = line.split(' ')[0]
                    ip = line.split(' ')[1]
                    port = int(line.split(' ')[2])
        
                    b = Branch(name, ip, port, 0)
                    self.branches[port] = b
        except IOError:
            print(sys.argv[2] + ": File not found")

    def __str__(self):
        return self.name + ': ' + 'balance=' + self.balance

    # Send a BranchMessage to Branch at port ; assumes BranchMessage is populated with the correct field
    def sendMessage(self, branch_message, port):
        if port not in self.branches.keys():
            print('Branch at port %i not found' % port)
            return False
        
        b = self.branches[port]
        try:
            b.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            b.sock.connect((b.ip, b.port))
            b.sock.send(branch_message.SerializeToString())
            b.sock.close()
        except:
            return False

        return True

        #b = self.branches[port]
        #try:
        #    b.sock.send(branch_message.SerializeToString())
        #    print('Sent message to port %i' % port)
        #except:
        #    print('Failed to send message to port %i' % port)
        #return True

    # Creates a TCP connection with all branches
    #def connectToAllBranches(self):
    #    for port in self.branches.keys():
    #        b = self.branches[port]
    #        try:
    #            b.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #            b.sock.connect((b.ip, b.port))
    #            print('Created a connection with port %i' % port)
    #            print('Controller info: ', b.sock.getsockname())
    #        except:
    #            print('Failed to connect to port %i' % port)

    ## Closes TCP connection with all branches
    #def closeAllConnections(self):
    #    for port in self.branches.keys():
    #        b = self.branches[port]
    #        try:
    #            b.sock.close()
    #            print('Closed connection with port %i' % port)
    #        except:
    #            print('Failed to close connection with port %i' % port)

    # Send InitBranch message to all branches
    def sendInitBranchToAll(self):
       
        if len(self.branches) <= 0:
            print('No branches to send balance.')
            return
  
        # Prepare InitBranch message to send to all branches
        ib = bank_pb2.InitBranch()
        
        # Add information about all other branches to BranchMessage
        for port in sorted(self.branches.keys()):
            b = self.branches[port]
            branch = ib.all_branches.add()
            branch.name = b.name
            branch.ip = b.ip
            branch.port = b.port
       
        ib.balance = self.balance / len(self.branches)

        for port in sorted(self.branches.keys()):
            
            # Create empty BranchMessage
            bm = bank_pb2.BranchMessage()
                       
            # Send InitMessage to this branch
            bm.init_branch.CopyFrom(ib)
            sent = self.sendMessage(bm, port)
            if sent:
                print('Sent InitBranch to port %i' % port)
            else:
                print('Failed to connect to branch at port %i' % port)

    # Sends InitSnapshot message to a random branch
    def sendInitSnapshot(self):
        port = sorted(self.branches.keys())[randint(0, len(self.branches.keys())-1)]
        b = self.branches[port]

        init_snapshot = bank_pb2.InitSnapshot()
        init_snapshot.snapshot_id = self.snapshot_id
        
        bm = bank_pb2.BranchMessage()
        bm.init_snapshot.CopyFrom(init_snapshot)
        #print('Sending InitSnapshot', bm)

        sent = self.sendMessage(bm, port)
        if sent:
            print('Sent InitSnapshot to port %i' % port)
        else:
            print('Failed to send InitSnapshot to port %i' % port)

    def sendRetrieveSnapshotToAll(self):
        r_snapshot = bank_pb2.RetrieveSnapshot()
        r_snapshot.snapshot_id = self.snapshot_id

        bm = bank_pb2.BranchMessage()
        bm.retrieve_snapshot.CopyFrom(r_snapshot)

        for port in self.branches.keys():
            # Don't use self.sendMessage() because this connection must be saved until snapshot is received
            b = self.branches[port]
            b.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            b.sock.connect((b.ip, b.port))
            sent = b.sock.send(bm.SerializeToString())
            if sent:
                print('Sent RetreiveSnapshot to port %i' % port)
            else:    
                print('Failed to send RetreiveSnapshot to port %i' % port)
            
    def getSnapshots(self):
        #print('Controller will start processing snapshots')
        # Get snapshots in name order 
        bnames = []
        for port in self.branches.keys():
            b = self.branches[port].name
            bnames.append(b)
        bnames.sort()

        snapshot_id = -1
        snapshots = []
        for bname in bnames: # extremely inefficient
            for port in self.branches.keys():
                b = self.branches[port]
                if b.name != bname:
                    continue
                
                message = b.sock.recv(4096)
                b.sock.close()
                
                bm = bank_pb2.BranchMessage()
                bm.ParseFromString(message)
                snapshots.append(bm.return_snapshot.local_snapshot)
                
                if snapshot_id == -1:
                    snapshot_id = bm.return_snapshot.local_snapshot.snapshot_id
                    print('---')
                    print('snapshot_id: %i' % snapshot_id)

        # print snapshots to console
        for i in range(0, len(bnames)):
            s = snapshots[i]
            bname = bnames[i]
            sys.stdout.write('%s: %i, ' % (bname, s.balance))           
 
            idx = 0
            num_printed = 0
            for b in bnames:
                if b == bname:
                    continue
                sys.stdout.write('%s->%s: %i' % (b, bname, s.channel_state[idx]))
                num_printed += 1
                if num_printed < len(bnames)-1:
                    sys.stdout.write(', ')

                idx += 1
            print('')

        print('---')

        self.snapshot_id += 1        
        return snapshots
        
    # should total the balance
    def checkSnapshots(self, snapshots):
        total = 0
        for s in snapshots:
            balance = s.balance
            channels = s.channel_state

            total += balance
            for c in channels:
                total += c

        print('Total = %i' % total)
        if total != self.balance:
            print('Balance = %i' % self.balance)
