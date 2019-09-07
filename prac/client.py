import socket
import sys

# Following this tutorial: https://www.geeksforgeeks.org/socket-programming-python/

# Create a socket
s = socket.socket()

# Port number should match server.py's port number
port = 12345

# Connect to server.py (on local computer)
try:
	s.connect(('127.0.0.1', port))
except:
	print('Failed to connect to port %i' % port)
	sys.exit()

# Retrieve data from server.py
data = s.recv(1024)
print('data: ', data)

# Close connection
s.close()
