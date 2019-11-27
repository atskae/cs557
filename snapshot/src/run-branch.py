#!/usr/bin/python3
import socket, random, sys, threading, time
from time import sleep

from Branch import Branch
from State import State

sys.path.append('/home/yaoliu/src_code/protobuf-3.7.0/python')
import bank_pb2

# global variable declaration
#runTransfer = False
initSnapshotFlag = False
markerFlag = False

def transfer(branch):
    #print('Transfer message at port %i' % branch.port)
    branchName = branch.name
    interval = branch.interval
    minPercent = 1
    maxPercent = 5
    
    numBranches = len(branch.branches)
    if numBranches > 0:
        # select receiveBranch
        port = sorted(branch.branches.keys())[random.randint(0, numBranches-1)]
        receiveBranch = branch.branches[port]

        # decrease balance
        percent = random.randint(minPercent,maxPercent) / 100.0
        amount  = int(branch.balance * percent)
        branch.updateBalance(False, amount)

        #output
        if branch.outputFlag:
            oldName = branchName
            newName = receiveBranch.name
            balance = branch.balance
            print('[**] Transfer %s -> %s (%i) Balance = %i [SENDING]' % (oldName, newName, amount, balance))

        # create transfer message
        transfer = bank_pb2.Transfer()
        transfer.send_branch = branchName
        transfer.amount = amount

        # attach transfer message to BranchMessage
        bm = bank_pb2.BranchMessage()
        bm.transfer.CopyFrom(transfer)

        # send transfer message
        branch.sendMessage(bm, port)

        # add update communication channel
        branch.updateCommChannel(receiveBranch.name, amount)
    else:
        print('[*] No branches to send messages')
        sys.exit(0)
        return

def startTransfer(branch):
    
    interval = branch.interval
    while True:
        #print("runTransfer=%s" % runTransfer)
        if branch.runTransfer:
            transfer(branch)
            time.sleep(interval)

def main():
    
    if len(sys.argv) != 4:
        print('Usage: ./branch <branch name> <port> <interval (ms)>')
        sys.exit(1)
            
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    name     = sys.argv[1]
    port     = sys.argv[2]
    interval = int(sys.argv[3]) * (10 ** -3) * 1.0
    
    # Create a Branch object at this port ; write branch information to branches.txt
    myBranch = Branch(name, ip, port, interval)
    myBranch.writeToBranchFile()   
 
    # Listen at port
    myBranch.listen()
    
    size = 9182
    msgNum = 0
    transferThread = threading.Thread(target=startTransfer, args=(myBranch,))
    transferThread.start() # runs forever
    while True:
        client, addr = myBranch.sock.accept()
        message = client.recv(size)

        # interpret message
        bm = bank_pb2.BranchMessage()
        bm.ParseFromString(message)

        if bm.HasField('init_branch'):
            print('[*] InitBranch Received at port %i' % myBranch.port)

            myBranch.balance = bm.init_branch.balance
            print('Branch at port %i received initial balance=%i' % (myBranch.port, myBranch.balance))            
 
            # store other branch info
            for b in bm.init_branch.all_branches:
                newBranch = Branch(b.name, b.ip, b.port, -1)
                if b.port != myBranch.port:
                    myBranch.branches[b.port] = newBranch

            # create a TCP connection with all branches
            #myBranch.connectToAllBranches()
            # Testing
            #myBranch.controller = (client, addr)
            #bm = bank_pb2.BranchMessage()
            #transfer = bank_pb2.Transfer()
            #transfer.send_branch = 'Pajama Sam'
            #transfer.amount = 4000
            #bm.transfer.CopyFrom(transfer)
            #myBranch.sendMessageToController(bm)
            #sys.exit()

            # start transfer thread
            myBranch.runTransfer = True
            #transferThread = threading.Thread(target=startTransfer, args=(myBranch,))
            #transferThread.start()

        elif bm.HasField('transfer'):
            
            amount = bm.transfer.amount
            sender = bm.transfer.send_branch
            myBranch.updateBalance(True, amount)

            # Update incomign channels
            myBranch.updateChannel(sender, amount)

            # output
            if myBranch.outputFlag:
                oldName = sender
                newName = name
                newBalance = myBranch.balance
                oldBalance = newBalance - amount
                print('[**] Transfer %s <- %s (%i) Balance = %i [RECEIVING]' % (oldName, newName, amount, newBalance))

            # remove message to communication channel
            myBranch.updateCommChannel(sender, 0)

        elif bm.HasField('init_snapshot'):
            print('[*] InitSnapshot received at port %i from Controller port %i' % (myBranch.port, addr[1]))

            snapshot_id = bm.init_snapshot.snapshot_id

            # Stop sending transfers
            print('init_snapshot, runTransfer=%s' % myBranch.runTransfer)
            myBranch.runTransfer = False
            #initSnapshotFlag = True
            #transferThread.join()

            # Send a Marker message to all branches
            myBranch.sendMarkerToAll(snapshot_id)
            myBranch.snapshot_id = snapshot_id

            # Restart transfers
            print('[**] Port %i Restarting transfers' % myBranch.port)
            myBranch.runTransfer = True

            #initSnapshotFlag = False
            #transferThread = threading.Thread(target=startTransfer, args=(myBranch,))
            #transferThread.start()

        elif bm.HasField('marker'):
            print('[*] Marker Received,')

            # extract marker info
            sender = bm.marker.send_branch
            snapshot_id = bm.marker.snapshot_id

            if snapshot_id not in myBranch.snapshots.keys():
                myBranch.snapshot_id = snapshot_id
                myBranch.runTransfer = False
                myBranch.snapshots[snapshot_id] = State(myBranch.branches, myBranch.balance, sender) # start recording all channels
                myBranch.sendMarkerToAll(snapshot_id)
                myBranch.runTransfer = True
            else:
                # Seen this marker ; stop recording this incoming channel
                myBranch.snapshots[snapshot_id].stopRecording(sender)

            # update snapshotDict
            #if myBranch.checkUniqueSnapshot(sender, snapshot_id):
            #    markerFlag = True
            #    myBranch.snapshot_id = snapshot_id
            #    myBranch.recordSnapshot()
            #    #transferThread.join()
            #    myBranch.runTransfer = False
            #    myBranch.sendMarkerToAll(snapshot_id)
            #    myBranch.runTransfer = True
            #    #transferThread = threading.Thread(target=startTransfer, args=(myBranch,))
            #else:
            #    myBranch.updateCommChannel(sender, 0)

        elif bm.HasField('retrieve_snapshot'):
            print('[*] RetrieveSnapshot received at port %i' % myBranch.port)

            # Save connection with Controller
            myBranch.controller = (client, addr)

            # extract retrieve_snapshot
            #snapshotID = bm.retrieve_snapshot.snapshot_id
                    
            # Test
            myBranch.sendReturnSnapshot()
        
        else:
            # this should never happen
            print('Received unknown BranchMessage', message)

        client.close()

if __name__ == '__main__':
    main()
