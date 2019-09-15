import socket
import sys
from _thread import *
import threading

from Request import *
from Server import Server

try:
	# AF_INET = use IPv4 ; SOCK_STREAM = Use TCP protocol
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	print('Failed to create a socket: %s' % (socket.err))
	sys.exit()

# Reserve a port for this server
# ? Is there a way to automatically find a free port?

# Create a server
server = Server(debug=True, host='', sock=sock, port=34567)

# maximum number of unaccepted connections before refusing new connnections
#max_pending = 5 # arbitrary number for now

# Bind the port
# Empty string (instead of an ip) listens for all incoming requests (as opposed to only listening for a specific ip)
#host = '127.0.0.1'
#host = ''

# Go to listening mode
server.listen(max_pending=5)
#s.listen(max_pending)
#logging.debug('Socket at port %i in listening mode...' % port)
#logging.debug('Clients can request with command: wget http://remote<XX>.cs.binghamton.edu:%i/<.html>' % port)

# resource name (ex. bar.html) -> # accesses
#res_counts = {}
#res_lock = threading.Lock()
#res_path = 'www'

# Infinitely listen for incoming TCP requests
while True:
	client_socket, addr = server.sock.accept()
	r = Request(client_socket.recv(1024), addr) # recv(# of bytes to read)
	#r.print_request()

	# start_new_thread(function, arguments as a tuple)
	start_new_thread(server.serve, (client_socket, r))

