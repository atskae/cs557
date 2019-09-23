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

# Create a server
server = Server(debug=False, host='', sock=sock, port=34567)

# Go to listening mode
server.listen(max_pending=5) # arbitary max_pending value

# Infinitely listen for incoming TCP requests
while True:
	client_socket, addr = server.sock.accept()
	r = Request(client_socket.recv(1024), addr) # recv(# of bytes to read)

	# start_new_thread(function, arguments as a tuple)
	start_new_thread(server.serve, (client_socket, r))
