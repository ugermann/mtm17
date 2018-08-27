#!/usr/bin/env python
from gen_client import MongoConn
import sys,datetime,socket
host="micha6f73000001" #mongo hostname

script=sys.argv[1]
model=sys.argv[2]
date=sys.argv[3]
out_trans=sys.argv[4]
out_name=sys.argv[5]
orig_corpus_name=sys.argv[6]
orig_corpus_src=sys.argv[7]
desc="Corpus created by backtranslation of %s with model %s"%(orig_corpus_name,model)
mongo=MongoConn(host=host)

mongo.create_corp(self,out_name,orig_corpus_src,out_trans,parents=[orig_corpus_name],desc=desc,operator="Backtranslation",direction="encs",type="training")



