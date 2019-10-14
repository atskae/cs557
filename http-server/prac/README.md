# Practice
Learning how to use sockets. The files in this directory are not needed to run the main project (and are primarily for myself).

## How to Run
1. Start the server by typing `python server.py`
2. In a different terminal window, request the server by typing `telnet localhost <port #>` where `<port #>` is the server's port number.
    * Or run `python client.py`
    * If testing on `remote.cs`, the client and server must be on the same remote node, since only local connections are accepted (see **Notes**).

## Notes
* To test client and server on `remote.cs` (where both client and server are on the same machine), `ssh` to the *same* `remoteXX` machine, where `XX` is a number between `00` and `07` (`00`, `01`, `02`, ... `07`). Example command: `ssh ashimiz1@remote00.cs.binghamton.edu`.
    * If `XX` is not specified, then you will be redirected to one of eight `remote` nodes.

## Resources
* [Socket Programming in Python](https://www.geeksforgeeks.org/socket-programming-python/)
