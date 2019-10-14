import socket
import sys

# Following this tutorial: https://www.geeksforgeeks.org/socket-programming-python/

try:
	# AF_INET = use IPv4 ; SOCK_STREAM = Use TCP protocol
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	print('Failed to create a socket: %s' % (socket.err))

# Reserve a port for this server
# ? Is there a way to automatically find a free port?
port = 12345

# maximum number of unaccepted connections before refusing new connnections
max_pending = 5

# Bind the port
# Empty string (instead of an ip) listens for all incoming requests (as opposed to only listening for a specific ip)
host = '127.0.0.1'
#host = ''
s.bind((host, port))

# Go to listening mode
s.listen(max_pending)
print('Socket at port %i in listening mode...' % port)

# Infinitely listen
while True:
	client_socket, addr = s.accept()
	print('Connected with address ', addr)

	# Send message to client
	client_socket.send('Thanks for connecting. Aufwiedersehen.')

	# Close the connection with client
	client_socket.close()
