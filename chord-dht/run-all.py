import sys
import subprocess
import os
import time
import hashlib

def getID(ip, port):
    return hashlib.sha256( (ip + ':' + str(port)).encode('utf-8') ).hexdigest()

RUN_CLIENT = False
try:
    if sys.argv[1] == '-c':
        RUN_CLIENT = True
except:
    pass

#print('RUN_CLIENT', RUN_CLIENT)
home = os.getcwd()

# Generate nodes.txt file
subprocess.call(['python', 'gen-nodes.py'])

# Start the DHT servers
servers = []
ids = {} # nodeID -> port #
c_port = None # port number that client uses
c_ip = None

f = open('nodes.txt', 'r')
os.chdir('py/')
for line in f:
    ip = line.split(':')[0]
    port = line.split(':')[1].replace('\n', '')
    if c_port is None:
        c_port = port
        c_ip = ip
   
    int_hash = int(getID(ip, int(port)), 16) 
    ids[int_hash] = int(port)
    #print('ip=%s, port=%s' % (ip, port)),
    
    args = ['./server.sh', port]
    try:
        #print('Launching ', args)
        servers.append(subprocess.Popen(args))
    except:
        print('Failed to launch ' , args)
os.chdir(home)
f.close()

# Initialize Finger Tables
time.sleep(1) # wait for all processes to start
print('Launching init')
subprocess.call(['./init', 'nodes.txt'])

# Run the client
if RUN_CLIENT is True:
    print('Launching client')
    os.chdir('py/')
    subprocess.call(['./client.sh', c_ip, c_port])
    os.chdir(home)
else:
    print('Running all DHT nodes indefinitely...')
    print('---')
    print('Chord DHT Ring')
    for i, k in enumerate(sorted(ids.keys())):
        print('%i: port=%i' % (i, ids[k]))
    print('---')
    while True:
        pass

# Terminate all servers
print('Terminating all DHT nodes')
for s in servers:
    s.kill()
