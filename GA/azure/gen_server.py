import SocketServer
import BaseHTTPServer
import json
import logging, time, re
logging.basicConfig(filename='test.log',level=logging.DEBUG)
import gen_params			
nematus_template=open('nematus_template.sh','r').read()

def expand_vars(params):
	m=None
	for p in params:
		m=re.match(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*',str(params[p]))
		print params.values()
		if m and str(m.group(0))[1:] in params:
			params[p]=params[p].replace(m.group(0),str(params[str(m.group(0)[1:])]))
			#if str(params[p]).find("$%s"%key)!=-1:
				#params[p]=params[p].replace("$%s"%key,str(params[key]))
	return params
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)	
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		"""Respond to a GET request."""
		logging.info("Recieved request from %s"%self.client_address[0])
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		
		#params=gen_params.Params().dict() # generovani parametru, v gen_params.py
		#params= expand_vars(params)
		#res=""
		
		#for p,v in params.iteritems():
		#	res+="%s=%s\n"%(p,v)
		#params['final_script']=nematus_template.replace('[INSERT_SETUP_HERE]',res)
		#params=expand_vars(params)
		#print (params)
		
		#send=json.dumps({k:v for k,v in params.iteritems()})
		task=self.server.mongo.getNext()
		print task
		send=json.dumps(task)
		self.send_header("Content-length", len(send))
		self.end_headers()

#		template=nematus_template.replace('[INSERT_SETUP_HERE]',res)
		logging.info("Sent model parameters to %s : %s"%(self.client_address[0],send))
		self.wfile.write(send)	       


if __name__ == '__main__':
	HOST='localhost'
	PORT=5001
	httpd = BaseHTTPServer.HTTPServer((HOST, PORT), MyHandler)
	httpd.mongo=MongoConn()

	print time.asctime(), "Server Starts - %s:%s" % (HOST, PORT)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print time.asctime(), "Server Stops - %s:%s" % (HOST, PORT)
	
#params=Params()
#with open("setup.sh",'w') as f:
#	for p,v in params:
#		f.write("%s=%s\n"%(p,v))
		
