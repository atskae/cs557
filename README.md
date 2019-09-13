# A Simple Multithreaded HTTP Server

## How to Run
1. Start the server by typing `python server.py`. The server will print out the port number where the server is listening for requests.
2. On a different remote node, send a request to the server by typing `wget http://remote<XX>.cs.binghamton.edu:<port #>/<file>`, where:
    * `<XX>`: the number of the remote node (ex. 00, 01, ..., 07)
    * `<port #>`: the port number where `server.py` is listening for incoming requests
    * `<file>`: the file to request from the server

## Files 
* `server.py`: Server that satisfies HTTP requests
* `Request.py`: HTTP request as a Python class

### Directories
* `www/`: contains content that the server can send to clients
* `prac/`: Practice code and notes (for myself) to learn how Python sockets work
