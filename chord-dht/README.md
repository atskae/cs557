# Chord Distributed Hash Table (DHT)
Chord DHT implemented using Apache Thrift and Python.

## Files and Directories
* `res/` Offline resources such as project description and Chord DHT paper.
* `py/` Contains the client and server and the Chord Python code generated by Thrift using `chord.thrift`
* `gen-nodes.py` Generates the `nodes.txt` file for `init`
* `run-all.py` Generates `nodes.txt`, starts the DHT nodes, launches `init`, then optionally runs `py/client.sh` or servers indefinitely. Use for testing.
* `init` Initializes the Finger Tables for each DHT node listed in `nodes.txt`

## How to Run
Steps 1-4 below can be executed automatically by running `python run-all.py`. The following steps can also be run manually:
1. Generate the `nodes.txt` file by running the command `python gen-nodes.py` or manually create a `nodes.txt` file, where each line is a `<IP address>:<port>` pair.
2. Run multiple servers (`py/server.sh <port>`) for each IP address and port number pair on each line in `nodes.txt` 
3. Run `init nodes.txt` to initialize the Finger Tables on the DHT servers
4. Run the client `py/client.sh` with the IP address used in Step 2 and any port number in `nodes.txt`

### Manually Run Client and a Single Server
1. Go to the `py/` directory by running the command `cd py/`
2. Start the server by running the command `./server.sh <port #>`, where `<port #>` is the port number where the server can listen for client requests.
3. Get the IP address by running the command `ip addr`. The IP address is listed in the format `inet IP address`.
4. Start the client by running the command `./client.sh <IP address> <port #>`, where `<IP address>` is the IP address obtained from Step 3, and `<port #>` is the port number where the server is listening for requests (Step 2).

## Notes
* I use the terms "DHT nodes" and "servers" interchangeably
* Implement the Chord functions (from `chord.thrift`) in `py/src/PythonServer.py`
* Not confident with `findPred()`. It usually returns the current node as the predecessor, which seems wrong. But when I print out the Finger Table, most of the port numbers repeat...
* Not confident on how I determine whether the 256-bit key is in a range...

## Resources
* [Chord DHT (paper)](https://pdos.csail.mit.edu/papers/ton:chord/paper-ton.pdf)
* Apache Thrift
    * [CS557 Thrift Lab](https://github.com/Yao-Liu-CS457-CS557/thrift-lab)
    * [Example Client and Server (Python)](http://thrift.apache.org/tutorial/py)
    * [Concepts](http://thrift.apache.org/docs/concepts)
    * [Features](http://thrift.apache.org/docs/features)
    * [Interface Definition Language (IDL)](http://thrift.apache.org/docs/idl)
    * [Thrift (paper)](https://thrift.apache.org/static/files/thrift-20070401.pdf)