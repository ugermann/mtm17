import xmlrpclib
import socket,time
class Client:
	def __init__(self,host,port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host,int(port)))
	def send(self,text):
		self.sock.sendall(text)
	def cmd(self,cmd):
		self.sock.sendall(cmd+'\n')
		r=self.sock.recv(4096)
		data=r
		#while len(r)>1023:
		#	r=self.sock.recv(1024)
		#	data+=r
		return data
	def close(self):
		self.sock.close()
	def readlines(recv_buffer=4096, delim='\n'):
		buffer = ''
		data = True
		while data:
			data =self.sock.recv(recv_buffer)
			buffer += data

			while buffer.find(delim) != -1:
				line, buffer = buffer.split('\n', 1)
				yield line
		return

class Translator:
	def __init__(self):
		self.url=None
		self.spec='encz'
	#set translation server
	def set_server(self,host,port):
		self.url='http://%s:%s' % (host,port)
	def translate(self,text):
		s = xmlrpclib.ServerProxy(self.url, verbose=False)
		data = { 'text': text,
			'word-align':True,
		#'nbest':1,
		}
		res=s.translate(data)
		return res
	def return_string(self):
		return 'RETURN encz %s' % (self.url)
		
cfgClient=Client('127.0.0.1',2401)
trans=Translator()
get= cfgClient.cmd('GET') #seznam alokacnich serveru
print get.split('\n')[0]

allocClient=Client(get.split(" ")[1],get.split(" ")[2])
dump=allocClient.cmd('DUMP')
print dump

use=allocClient.cmd('HIRE encz 1')
print use
while use.startswith('BUSY'):
	print "Obsazeno, cekam"
	time.sleep(1)
	use=allocClient.cmd('HIRE encz 1')
	print use


if use.startswith('UNAVAILABLE'):
	print "Tohle nepujde"

elif use.startswith('USE'):
	pass # v klidu
else:
	print "Toto se nestane"

transPort=use.split(" ")[3].split(":")[1]
transIP=use.split(" ")[3].split(":")[2].replace('\n','')

print transIP
print transPort
trans.set_server(transIP,transPort)
text = "A sentence with more than one possible translation ."
res=trans.translate(text)

print allocClient.cmd(trans.return_string())

allocClient.close()
cfgClient.close()

response_body=unicode(res['text'])
for a in res['word-align']:
	response_body+='%s-%s ' % (a['source-word'], a['target-word'])
print response_body

