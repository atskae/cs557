'''
Generates a nodes.txt file for the init program to initialize Finger Tables
for the DHT nodes
'''

import sys
import socket
import random

outfile = 'nodes.txt'
num_nodes = 2
port = random.randint(50000, 65535)
try:
    num_nodes = int(sys.argv[1])
    port = int(sys.argv[2])
except:
    pass

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
print('Generating %i DHT nodes at IP address %s starting at port %i' % (num_nodes, ip, port))

f = open('nodes.txt', 'w')
for i in range(0, num_nodes):
    line = ip + ':' + str(port) + '\n'
#    print('%2i: %s' % (i, line)),
    f.write(line)
    port += 1
f.close()

print('Saved to %s' % outfile)
