#!/usr/bin/env python
import pymongo
import httplib


import subprocess
import json,os
import datetime
import logging, time
import socket
from bson import json_util
from dbutil import MongoConn
#nematus_template=open('nematus_template.sh','r').read()
from nltk.translate.gleu_score import sentence_gleu


 #python_interpreter="/share/michal/env/bin/python2.7"
#python_interpreter="/usr/bin/python"

def computeGleu(target,reference):
    return [sentence_gleu([ref],tgt) for (ref,tgt) in zip(reference,target)]

def computeGleuDifference(gleu_src,gleu_tgt):
    return sum([(float(src)-float(tgt))**2 for (src,tgt) in zip(gleu_src,gleu_tgt)])
def construct_doc(params, metric, score, translated):
     #, model_path,cfg_path, corp_src, corp_tgt, test_src, test_tgt, eval_metric, eval_score
    model_path=params['model_path'].replace('$data_dir',params['data_dir'])
    cfg_path=".".join([model_path,'json'])
    src_train=params['src_train'].replace('$data_dir',params['data_dir'])
    tgt_train=params['tgt_train'].replace('$data_dir',params['data_dir'])
    src_val=params['src_val'].replace('$data_dir',params['data_dir'])
    tgt_val=params['tgt_val'].replace('$data_dir',params['data_dir'])
    translated=translated
    eval_metric=metric
    eval_score=score


    doc={"ModelPath":model_path,
        "Config":cfg_path,

        "TrainingCorpus":{	"source":src_train,
                            "target":tgt_train},

        "TestCorpus":{	"source":src_val,
                        "target":tgt_val},

        "Evaluation": {
                        "translation":translated,
                        "metric":eval_metric,
                        "score":eval_score}
        }
    return doc

if __name__=='__main__':
    #validate_template=open('validate_template.sh','r').read()

    #conn = httplib.HTTPConnection("localhost",5001)
    #conn.request("GET", "/")
    ##res=""
    #res=conn.getresponse()
    #print(res.getheaders())
    #try:
        #params = json.loads(res.read())
    #except Exception as e:
        #print (e)
    #print params
    #TADY POSLAT POTVRZENI TASK SERVERU, ZE MUZE ULOHU PREPNOUT DO STAVU PENDING(nebo to sam zmenit v db, asi lepsi)

    #print params

    #for p,v in params.iteritems():
    #		res+="%s=%s\n"%(p,v)
    #template=validate_template.replace('[INSERT_SETUP_HERE]',res)
    #mongo=MongoConn(host="micha6f73000001")
    mongo=MongoConn(host="localhost")

    #mongo.createNode()
    while True:
        task=mongo.getNextTask()

        try:
            print "Got task:"
            print task
            objID=task["_id"]
        except:
            print "No task or something else went wrong. Waiting for 5 min"
            time.sleep(300)
            args = ['python gen_client.py', "%s/gen_client.py" % os.getcwd()]
            e = os.environ
            e["PATH"] = ':'.join((e["PATH"], "/mnt/nfs/env"))
            os.execlpe("./gen_client.py", ' '.join(args), e)
            exit()
            #exit()
        mongo.TaskToNode(objID)

        #mongo.startTask(objID)
        date=datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S.%f")
        runScriptsFg=[]
        runScriptsBg=[]
        supportScripts=[]
        ret=-1
        for name,script in task["Scripts"]["RunScriptsFg"].iteritems():
            f=open("%s%s.sh"%(name,date),"w")
            f.write(script.replace("$client_date",date))
            f.close()
            subprocess.Popen(['chmod','+x',"%s%s.sh"%(name,date)],stdout=subprocess.PIPE)
            runScriptsFg.append("%s%s.sh"%(name,date))

        for name,script in task["Scripts"]["SupportScripts"].iteritems():
            f=open("%s%s.sh"%(name,date),"w")
            f.write(script.replace("$client_date",date))
            f.close()
            subprocess.Popen(['chmod','+x',"%s%s.sh"%(name,date)],stdout=subprocess.PIPE)
            supportScripts.append("%s%s.sh"%(name,date))


        for script in runScriptsFg:
            proc = subprocess.Popen(['bash',script],stdout=subprocess.PIPE)
        ##FAIL
            proc.wait()
            ret=proc.returncode
            if ret!=0:
                print "Task failed. Return code %s" %proc.returncode
                mongo.failTask(objID,proc.returncode,proc.communicate()[1])

        if ret==0:
            mongo.finishTask(objID)
        print "Task done"
        mongo.NodeTaskDone()
    #proc.wait()
        #score= proc.communicate()[0]
        #if task["Type"]=="Evaluation":
         #   #pass
          #  score=proc.communicate()[0].split('\n')[-2]
           # mongo.saveEval(construct_doc(params,'BLEU',score,translated="TBD"))

        #conn.close()
        #os.system("python gen_client.py")
        args = ['python gen_client.py',"%s/gen_client.py" % os.getcwd()]
        e=os.environ
        e["PATH"]=':'.join((e["PATH"],"/mnt/nfs/env"))
        os.execlpe("./gen_client.py", ' '.join(args),e)
        exit()
