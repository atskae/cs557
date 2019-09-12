# HTTP Request format: https://www.tutorialspoint.com/http/http_requests.htm

class Request:

	request = '' # raw string
	host = ''
	port = ''
	method = '' # GET, POST, etc.
	url = '' # the requested webpage ex) bar.html
	http_ver = '' # HTTP version
	header_fields = {}
	message_body = ''
	
	def __init__(self, request, addr):

		self.request = request
		self.host = addr[0]
		self.port = addr[1]
	
		# Parse HTTP request
		rq = self.request.replace('\n', '').split('\r') 	

		# Request-Line
		line = rq[0].split(' ')
		self.method = line[0]
		self.url = line[1]
		self.http_ver = line[2]

		for i in range(1, len(rq) - 2):
			fields = rq[i].split(': ')
			self.header_fields[fields[0]] = fields[1]
	
		self.message_body = rq[len(rq) - 1]

	def print_request(self):
		print('Host %s at Port %s' % (self.host, self.port))
		print('Method: %s' % self.method)
		print('Requested URL: %s' % self.url)
		print(self.header_fields)
		if self.message_body != '':
			print('Message body: %s' % self.message_body)
