#!/usr/bin/python3
import time, socket, sys, threading
from State import State

sys.path.append('/home/yaoliu/src_code/protobuf-3.7.0/python')
import bank_pb2

class Branch:
    name = None
    ip = None
    port = None
    interval       = 0  # miliseconds between transfer messages
    branches       = {} # port number -> Branch object
    outputFlag = True
    listen_sock = None # Only used by the controller to retreive snapshots from Branches

    runTransfer = False

    controller = None
 
    snapshotBalance = 0
    balance        = 0
    commChannel    = {} # commChannel[sender] = amount
    snapshotDict   = {} # snapshotDict[(sender, snapshotID)] = whatever
    localStateList = [] # list of recorded local states
    lock = None

    snapshot_id = None # Set if currently recording
    snapshots = {} # snapshot_id -> state
    
    sock = None
    max_pending = 5 # arbitrary value

    def __init__(self, name, ip, port, interval):
        self.name = name # string name ; ex. 'branch1'
        self.ip = ip
        self.port = int(port)
        self.interval = interval
        self.lock = threading.Lock()
        
        if self.interval > 1000:
            outputFlag = True

    def __str__(self):
        return self.name + ': ' + 'ip=' + self.ip + ', port=' + str(self.port) + ', interval=' + str(self.interval) + 'ms'

    def writeToBranchFile(self):
        with open('branches.txt', 'a') as f:
            f.write(self.name + ' ' + self.ip + ' ' + str(self.port) + '\n')

    def listen(self):
        try: # AF_INET = use IPv4 ; SOCK_STREAM = Use TCP protocol
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.ip, self.port))
        except:
            print('Failed to create TCP connection at port %i' % self.port)
            return

        self.sock.listen(self.max_pending)
        print('%s in listening at port %i...' % (self.name, self.port))

    # Creates a TCP connection with all branches
    def connectToAllBranches(self):
        for port in self.branches.keys():
            b = self.branches[port]
            try:
                b.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                b.sock.connect((b.ip, b.port))
                print('%s created a connection with %s' % (self.name, b.name))
            except:
                print('%s failed to connect to %s' % (self.name, b.name))

    def sendMessageToController(self, branch_message):
        if self.controller is None:
            print('No information on the Controller')
            return

        controller, addr = self.controller
        try:
            print('Sending', branch_message)
            controller.send(branch_message.SerializeToString())
            print('%s sent message to Controller' % self.name)
        except:
            print('%s failed to send message to Controller' % self.name)
 
    # Send a BranchMessage to Branch at port ; assumes BranchMessage is populated with the correct field
    def sendMessage(self, branch_message, port):
        if port not in self.branches.keys():
            print('Branch at port %i not found' % port)
            return False

        b = self.branches[port]
        b.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        b.sock.connect((b.ip, b.port))
        b.sock.send(branch_message.SerializeToString())
        b.sock.close()

        ##try:
        #print('%s will send message to port %s' % (self.name, b.name))
        #print(branch_message)
        #b.sock.send(branch_message.SerializeToString())
        #except:
        #    print('%s failed to send message to port %i' % (self.name, port))
        #    sys.exit()
        #    return False

        return True
 
    def updateChannel(self, sender, amount):
        if self.snapshot_id in self.snapshots.keys(): # started recording this snapshot_id
            s = self.snapshots[self.snapshot_id]
            if s.isRecording(sender):
                s.updateChannel(sender, amount)

    def handleMarkerMessage(self):
        self.lock.acquire()

    def updateBalance(self, incFlag, amount):
        try:
            self.lock.acquire()
            if incFlag:
                self.balance += amount
            else:
                self.balance -= amount
            self.lock.release()
        except ThreadError:
            print('\t[FATAL ERROR 0')
            print('\tBranch:updateBalance()')
            print('\tlock was already released')
            sys.exit(1)

    def sendMarkerToAll(self, snapshot_id):
        # Send a Marker message to all branches
        for port in self.branches.keys():
            if port == self.port:
                continue

            # Create empty BranchMessage
            bm = bank_pb2.BranchMessage()

            marker = bank_pb2.Marker()
            marker.send_branch = self.name
            marker.snapshot_id = snapshot_id

            # Attach Marker to BranchMessage
            bm.marker.CopyFrom(marker)

            sent = self.sendMessage(bm, port)
            if sent:
                print('Sent Marker to port %i from port %i' % (port, self.port))

    def updateCommChannel(self, branch, amount):
        try:
            self.lock.acquire()
            self.commChannel[branch] = amount
            self.lock.release()
        except ThreadError:
            print('[FATAL ERROR] 0')
            print('\tBranch:updateCommChannel()')
            print('\tlock was already released')
            sys.exit(1)

    def getLocalState(self):
        name = self.name
        try:
            self.lock.acquire()
            balance = self.balance
            self.lock.release()
        except ThreadError:
            print('[FATAL ERROR] 0')
            print('\tBranch:getLocalState()')
            print('\tlock was already released')
            sys.exit(1)

        branchSize = len(self.branchList)
        output = name + ': ' + str(balance) + ', '

        for branch, amount in self.commChannel.items():
            output += branch + '->' + name + ': ' + str(amount) + ' '
        return output

    # TODO test me
    def checkUniqueSnapshot(self, sender, snapshotID):
        output = True
        myTuple = (sender, snapshotID)
        try:
            self.lock.acquire()
            if self.snapshotDict.has_key(myTuple):
                output = False
            else:
                self.snapshotDict[myTuple] = 0

            self.lock.release()
        except ThreadError:
            print('[FATAL ERROR] 0')
            print('\tBranch:checkUniqueSnapshot()')
            print('\tlock was already released')
            sys.exit(1)
        finally:
            return output

    # TODO test me
    def recordSnapshot(self):
        for branch, value in self.commChannel.items():
            self.commChannel[branch] = 0

        try:
            self.lock.acquire()
            self.snapshotBalance = self.balance
            self.lock.release()
        except ThreadError:
            print('[FATAL ERROR] 0')
            print('\tBranch:checkUniqueSnapshot()')
            print('\tlock was already released')
            sys.exit(1)

    def sendReturnSnapshot(self):
        snapshot = bank_pb2.ReturnSnapshot()
        snapshot.local_snapshot.snapshot_id = self.snapshot_id
        #snapshot.local_snapshot.balance = self.snapshotBalance
        snapshot.local_snapshot.balance = self.snapshots[self.snapshot_id].balance

        # First get senders in sorted order
        senders = []
        for port in self.branches.keys():
            sender = self.branches[port].name
            senders.append(sender)
        senders.sort() 
        
        channel_states = []
        for sender in senders:
            amount = self.snapshots[self.snapshot_id].getChannel(sender)
            channel_states.append(amount)
        
        #for branch in sorted(self.commChannel.keys()):
        #    #snapshot.local_snapshot.channel_state.extend(self.commChannel[branch])
        #    channel_states.append(self.commChannel[branch])

        snapshot.local_snapshot.channel_state.extend(channel_states)
        bm = bank_pb2.BranchMessage()
        bm.return_snapshot.CopyFrom(snapshot)

        print('ReturnSnapshot to send to Controller', bm)
        
        # Send to Controller
        self.sendMessageToController(bm)
