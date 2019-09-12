import socket
import sys
import logging # debug print statements

from Request import Request

# Set up debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.DEBUG)
logging.debug('Debug logging turned ON.')

try:
	# AF_INET = use IPv4 ; SOCK_STREAM = Use TCP protocol
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	print('Failed to create a socket: %s' % (socket.err))
	sys.exit()

# Reserve a port for this server
# ? Is there a way to automatically find a free port?
port = 34567

# maximum number of unaccepted connections before refusing new connnections
max_pending = 5 # arbitrary number for now

# Bind the port
# Empty string (instead of an ip) listens for all incoming requests (as opposed to only listening for a specific ip)
#host = '127.0.0.1'
host = ''
s.bind((host, port))

# Go to listening mode
s.listen(max_pending)
#print('Socket at port %i in listening mode...' % port)
logging.debug('Socket at port %i in listening mode...' % port)
logging.debug('Clients can request with command: wget http://remote<XX>.cs.binghamton.edu:%i/<.html>' % port)

# Infinitely listen for incoming TCP requests
while True:
	client_socket, addr = s.accept()
	logging.debug('Connected with host %s at port %s' % (addr[0], addr[1]))
	#print('Connected with address %s at port %s' % (addr[0], addr[1]))

	r = Request(client_socket.recv(1024), addr) # recv(# of bytes to read)
	r.print_request()

	print("%s|%s|%s|%i" % (r.url, r.host, r.port, -1))

	# Send message to client
	client_socket.send('Thanks for connecting. Aufwiedersehen.')

	# Close the connection with client
	client_socket.close()
	logging.debug('Closed connection')
