#!/usr/bin/python3
#File: BankBranch
#Version: python3.7.4
#Import--------------
import socket, random
#Import--------------
class BankBranch:
    def __init__(self):
        self.transferDict = ""  #<branchName, transferAmount>
        self.branchList = ""    #list[BankBranch]
        self.branchName = ""
        self.localState = ""
        self.interval = ""
        self.tcpDict = ""       #<branchName, branchSocket>
        self.balance = ""
        self.port = ""
        self.ip = ""

    //initBranch

    //

    //start
    //used to transfer money amongst other branches
    def start(self):
        //variable declaration
        branchName = this.branchName

        while True:
            if balance > 0:
                #select branch
                randIndex = random.randint(0, len(transferDict) - 1)
                otherBranch = self.branchList[randIndex]

                #select amount
                randPercent = random.randint(1, 5)
                amount = balance * randPercent

                #transfer
                otherBranch.transfer(amount, branchName)

                #record local state
                self.recordLocalState()

    //recordLocalState
    //records local state for the respected branch
    //  local state matches the following format
    //  <branch name>: <branch balance>, <next branch>-><branch name>, ...
    def recordLocalState(self):
        //variable declaration
        otherBranch = ""
        branchName = self.branchName
        newLine = "\n"
        rArrow = "->"
        output = ""

        //add branch name and balance to output
        output += branchName + ": " + self.balance + ", "

        //add branch transfer to output
        branchNum = len( self.tcpDict )
        for x in range(branchNum):
            otherBranch = self.BranchList[x]
            output += otherBranch + rArrow + branchName + ": "
            if self.transferDict.has_key(otherBranch):
                output += self.transferDict[otherBranch] + newLine
            else:
                print("[ERROR]:",otherBranch,"is not in transferDict")
                sys.exit(1)


        //set local state
        self.localState = output
