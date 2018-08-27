import pymongo
import httplib
import subprocess
import json,os
import logging,sys
sys.path.append('../')
from gen_client import MongoConn
import gen_server
#nematus_template=open('../nematus_template.sh','r').read()
population=20                 
	
conn = httplib.HTTPConnection("localhost",5001)
def construct_doc(params):
	doc={}
	doc=expand_vars(params)

	return {'ModelTraining':doc}
	

for x in range(population):
	conn.request("GET", "/")
	res=""
	model_id=x
	res=conn.getresponse()
	print(res.getheaders())
	params = json.loads(res.read())
	params["model_name"]="model%s.npz"%x
	params["model_id"]="%s"%x
	params=gen_server.expand_vars(params)
	#print params

	#for p,v in params.iteritems():
			#res+="%s=%s\n"%(p,v)
	#res+="model_name=model%s\n"%x
	#res+="model_id=%s"%x

	#template=nematus_template.replace('[INSERT_SETUP_HERE]',res)
	script=params["final_script"]
	f=open("train%s.sh"%x,"w")
	f.write(script)
	f.close()
	proc = subprocess.Popen(['nohup','bash', 'train%s.sh'%x],stdout=open('train%s.out'%x, 'a'),stderr=open('train%s.err'%x, 'a'),preexec_fn=os.setpgrp)
	#proc.wait()
	#score= proc.communicate()[0]
	mongo=MongoConn()
	mongo.insert(params)

	conn.close()
