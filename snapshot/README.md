# Chandly-Lamport Snapshot Algorithm


### Send a Branch Messsage
Every message is sent inside of a `BranchMessage`.

1. On the sender side, first create an empty BranchMessage:
`branchMessage = bank_pb2.BranchMessage()`

2. Then choose a message type from the `bank.proto` file that you want to send. For example, if I want to send a `InitBranch` message, create an empty InitBranch:
`ib = bank_pb2.InitBranch()`

3. After populating the message (for example, calling `add()` on the InitBranch messsage to populate its fields), set the message in the BranchMessage. For example, if I want to set the `InitBranch` that I created in Step 2:
`branchMessage.init_branch.CopyFrom(ib)`

4. Serialize the message to a string:
`branchMessage.SerializeToString()`

Then send this string through the TCP connection to the receiver.

### Receiving a Branch Message
1. Receive the message from the TCP connection:
`message = client.recv(1024)`

2. Create an empty Branch Message
`branchMessage = bank_pb2.BranchMessage()`

3. Parse the message from Step 1 as a Branch Message
`branchMessage.ParseFromString(message)`

4. Decode the message by checking which field in the Branch Message is populated. For example, if I wanted to see if this message was an InitBranch message:
`if branchMessage.HasField("init_branch") is True`

References
* [How to set oneof fields in Python?](https://github.com/protocolbuffers/protobuf/issues/5012)
* [Python Generated Code: oneof](https://developers.google.com/protocol-buffers/docs/reference/python-generated#oneof)

## Compile and Run Code
### Setup Environment
```
./setup_env
make
mv bank_pb2.py src/
```
### Run Branch (run individually)
```
./branch <branch name> <port> <interval>
```
### Run Multiple Branches Automatically
Run `run-branches.py` to automatically start branches at random ports. Running the branches will create the `branches.txt` file, which the controller needs to read.
```
python run-branches.py <# of branches>
```
`# of branches` is optional. The default value is 4, which can be changed in the script.

Once the branches are listening to the ports, the controller can be run.

### Run Controller (add branch info manually in "branches.txt")
```
./controller <branch sum> branches.txt
```
#### "branches.txt" Template
```
<branch name> <ip address> <port>
```
