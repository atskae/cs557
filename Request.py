class Request:

	request = '' # raw string
	method = '' # GET, POST, etc.
	url = '' # the requested webpage ex) bar.html
	http_ver = '' # HTTP version
	header_fields = {}
	message_body = ''
	
	def __init__(self, request):

		self.request = request
		
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
		print('Method: %s' % self.method)
		print('Requested URL: %s' % self.url)
		print(self.header_fields)
		if self.message_body != '':
			print('Message body: %s' % self.message_body)
