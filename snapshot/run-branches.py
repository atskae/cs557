import sys, subprocess, os, time, random

num_branches = 3
try:
    if int(sys.argv[1]):
        num_branches = int(sys.argv[1])
except:
    pass

port = random.randint(50000, 65535)
interval = 10 # miliseconds
bfile = 'branches.txt'
branches = [] # branch processes

# If branches.txt exits, remove it and create a new one
if os.path.exists(bfile):
    print('Removing old %s file' % bfile)
    os.remove(bfile)

# Launch the branches
failed = 0
for i in range(0, num_branches):
    name = "branch" + str(i)
    args = [sys.executable, 'src/run-branch.py', name, str(port), str(interval)]
    try:
        branches.append(subprocess.Popen(args))
        time.sleep(1) # wait until branch writes to branches.txt file
    except:
        print('Failed to launch ' , args)
        failed += 1
    
    port += 1   

# Check if branches.txt file was created
if os.path.exists(bfile):
    print("%s file was created. %i/%i branch nodes listening..." % (bfile, len(branches)-failed, len(branches)))
else:
    print('Failed to create %s' % bfile)
    sys.exit(1)

while True:
    pass

# Terminate all servers
print('Terminating all branch nodes')
for b in branches:
    b.kill()
