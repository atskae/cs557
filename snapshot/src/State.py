class State():
    balance = 0
    ichannels = {} # incoming channels to this branch ; branch name -> money received
    record = {} # sender -> True/False

    # Created when Marker is first seen
    def __init__(self, branches, balance, sender):
        self.balance = balance
        self.ichannels[sender] = 0 # sender's incoming channel is set to empty

        # start recording
        for port in branches.keys():
            sender = branches[port].name
            self.record[sender] = True

    def updateChannel(self, sender, amount):
        if sender not in self.ichannels.keys():
            self.ichannels[sender] = amount
        else:
            self.ichannels[sender] += amount
   
    def isRecording(self, sender):
        return self.record[sender]
 
    def stopRecording(self, sender):
        self.record[sender] = False

    def getChannel(self, sender):
        if sender in self.ichannels.keys():
            return self.ichannels[sender]
        else:
            return 0
