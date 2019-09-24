# A Simple Multithreaded HTTP Server


## How to Run
1. Start the server by typing `python run.py`. The server will print out the host name and port number where the server is listening for requests. The following is an example initial output by the server:
    `Server in listening mode at host remote03, port 34567...`
2. On a different remote node, send a request to the server by typing `wget http://remote<XX>.cs.binghamton.edu:<port #>/<file>`, where:
    * `<XX>`: the number of the remote node (ex. 00, 01, ..., 07) of the host
    * `<port #>`: the port number where `run.py` is listening for incoming requests
    * `<file>`: the file to request from the server

# Example Run
We can request the file `gutentag.txt` from the server with host name `remote03` at port `34567` by typing: `wget http://remote03.cs.binghamton.edu:34567/gutentag.txt`.
The server should print out `/gutentag.txt|128.226.114.205|50902|1`, which has the format `<requested file>|<client's IP address>|<client's port #>|<count>`. The client should print out the following if successful:
```
--2019-09-23 20:32:07--  http://remote03.cs.binghamton.edu:34567/gutentag.txt
Resolving remote03.cs.binghamton.edu (remote03.cs.binghamton.edu)... 128.226.114.203
Connecting to remote03.cs.binghamton.edu (remote03.cs.binghamton.edu)|128.226.114.203|:34567... connected.
HTTP request sent, awaiting response... 200 OK
Length: 23 [text/plain]
Saving to: ‘gutentag.txt’

gutentag.txt                                       100%[================================================================================================================>]      23  --.-KB/s    in 0s      

2019-09-23 20:32:07 (3.99 MB/s) - ‘gutentag.txt’ saved [23/23]
```
The file `gutentag.txt` should be in the client's directory after the request.

## Files 
* `run.py`: Creates a server object and starts listening for requests
* `Server.py`: Server class that satisfies HTTP requests
* `Request.py`: HTTP request class containing request metadata

### Directories
* `www/`: Contains content that the server can send to clients
* `prac/`: Practice code and notes (for myself) to learn how Python sockets work
