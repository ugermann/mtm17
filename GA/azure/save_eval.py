#!/usr/bin/env python
from gen_client import MongoConn
import sys,datetime,socket
host="micha6f73000001" #mongo hostname
script=sys.argv[1]
model=sys.argv[2]
date=sys.argv[4]
try:
    outfile=sys.argv[5]
except:
    outfile=None
try:
    val_src=sys.argv[6]
except:
    val_src=None

try:
    val_tgt=sys.argv[7]
except:
    val_tgt=None

try:
    desc=sys.argv[8]
except:
    desc=None
metric="BLEU"
score=float(sys.argv[3])
source=open(script,'r').read()
doc={"Model":model,
	"Host":socket.gethostname(),
	"Date":datetime.datetime.now(),
	"Script":source,
	"Metric":metric,
	"Score":score,
    "ValSrc":val_src,
	 "Description": desc,

	 "ValRef":val_tgt,
    "Output": open(outfile).read()}
mongo=MongoConn(host=host)
mongo.saveEval(doc)

