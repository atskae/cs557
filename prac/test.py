import socket
import sys

# Following this tutorial: https://www.geeksforgeeks.org/socket-programming-python/

try:
	# AF_INET = use IPv4 ; SOCK_STREAM = Use TCP protocol
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	print('Failed to create a socket: %s' % (socket.err))

host_url = 'www.binghamton.edu'
try:
	# Get IP address
	host_ip = socket.gethostbyname(host_url)
	print('host_url=%s, host_ip=%s' % (host_url, host_ip))
except socket.gaierror:
	print('Failed to get host_ip address of %s' % (host_ip, host_url))
	sys.exit()

# Default port
port = 80

# Create a connection
s.connect((host_ip, port))
print('Connected to port %s' % (host_ip))
