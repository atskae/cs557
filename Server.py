import socket
import logging
import threading

# serve() and Request class
from Request import *

# Date in RFC format: https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
def get_date():
	now = datetime.now()	
	stamp = mktime(now.timetuple())
	return format_date_time(stamp)

class Server:
	name = 'johto' # Name of the server

	host = '' # Empty string (instead of an ip) listens for all incoming requests (as opposed to only listening for a specific ip)
	sock = None # Socket to listen for incoming clients
	port = 2048
	max_pending = 5

	res_counts = {}
	lock = None
	res_path = 'www'

	def __init__(self, debug, host, sock, port):
		self.host = host
		self.sock = sock
		self.port = port
		self.lock = threading.Lock()
	
		self.sock.bind((host, port))

		# Set up debug logging
		if debug is True:
			logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
			logging.debug('Debug logging turned ON.')
		else:
			logging.disable(logging.DEBUG)

	# Go into Listening Mode
	def listen(self, max_pending):
		self.max_pending = max_pending
		
		self.sock.listen(max_pending)
		logging.debug('Socket at port %i in listening mode...' % self.port)
		logging.debug('Clients can request with command: wget http://remote<XX>.cs.binghamton.edu:%i/<.html>' % self.port)

	def serve(self, client_sock, r): 
		logging.debug('Connected with host %s at port %s' % (r.host, r.port))
		
		# check if self.resource exists
		path = self.res_path + r.res
		f = None
		try:
			f = open(path, 'r')
		except:
			logging.debug('%s does not exist.' % path)
			# send error message to client
			client_sock.send(r.http_ver + ' ' + '402 Not Found')
			client_sock.close()
			return
	
		# Prepare response
		response = ''
		response += (r.http_ver + ' 200 OK\n')
		response += ('Date: ' + get_date() + '\n')
		response += ('Last-Modified: ' + str(os.path.getmtime(path)) + '\n')
		response += ('Content-Type: ' + '\n')
		response += ('Content-Length: ' + '-1\n')
		logging.debug('Response:\n%s' % response)
	
		# Send requested file to client
		client_sock.sendall(f.read())
		f.close()
	
		self.lock.acquire()
		if r.res not in self.res_counts.keys():
			self.res_counts[r.res] = 0
		self.res_counts[r.res] += 1	
		print("%s|%s|%s|%i" % (r.res, r.host, r.port, self.res_counts[r.res]))
		self.lock.release()
	
		# Close the connection with client
		client_sock.close()
		logging.debug('Closed connection')
	
