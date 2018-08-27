import pymongo
import httplib
import subprocess
import json,os
import datetime
import logging, time, re
import socket
from bson import json_util
class MongoConn():
    
    def __init__(self, host='localhost', port=27017):
        #192.168.203.57
        self.host = host
        # self.spec=spec
        self.port = port
        self.dbname = 'local'
        self.running=False
        self.connect(host, port)

    def connect(self, host, port):
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[self.dbname]
        try:
           # self.db.authenticate('root', 'mar19a10', source='admin')
            self.client.database_names()
            self.running = True
        except Exception as e:
            logging.error('Cant connect to mongodb: %s' % e)
            self.running = False
        except pymongo.errors.OperationFailure as e:
            logging.error('Cant login to mongodb: %s' % e)
            self.running = False

    def insert(self, doc,collection='GA'):
        return self.db[collection].insert_one(doc)
    def get_model_host(self,model_name):
        try:
            return self.db.Tasks.find_one({"Model":model_name},sort=[("StartDate",pymongo.ASCENDING)])["Host"]#.sort("StartDate")[0]["Host"]
        except Exception as e:
            raise e
            #return None
    def add_operator(self,params):
        maxi=self.db.Operators.find().count()
        o=params
        o["OperatorID"]=maxi+1
        #type, source code? Dalsi modely by pak mely pole parents a polozku operator, aby se vytvorit jejich strom
        self.db.Operators.save(o)
    
    def generateTask(self,doc):
        return self.insert(doc,collection='Tasks')


    def saveEval(self,doc):
        return self.insert(doc,collection='Evaluation')
    
    def get(self, expr, collection='GA'):
        try:
            return self.db[collection].find_one(expr)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.error('mongo error:  %s' % e)
            return None


    def createModel(self, params):
        doc={		"ModelID":params["model_id"],
				"params":params}
        assert "marian_home" in params
        assert "moses_home" in params

        return self.insert(doc,collection="Models")

    def getNextTask(self,ttype=None):
        #res=self.db['Tasks'].find({"State": "Waiting"}).sort("_id")
        if ttype:
			res=self.db['Tasks'].find_one_and_update({"State": "Waiting","Type":ttype},{"$set": {"State": "Pending", "StartTime":datetime.datetime.now(), "Host":socket.gethostname()}},sort=[("Priority",1)("_id",1)])
        else:
			res=self.db['Tasks'].find_one_and_update({"State": "Waiting"},{"$set": {"State": "Pending", "StartTime":datetime.datetime.now(), "Host":socket.gethostname()}},sort=[("Priority",1),("_id",1)]) # documents are sorted by creation timestamp by default
        return res#[0]
    #def startTask(self,obj_id):
     #   res=self.db['Tasks'].update_one({"_id":obj_id},{"$set": {"State": "Pending"}})
      #  return res

    def failTask(self,obj_id,err,stderr):
        res=self.db['Tasks'].update_one({"_id":obj_id},{"$set":  {"State": "Failed", "StopTime":datetime.datetime.now(), "Error":err, "Stderr":stderr,"Host":socket.gethostname()}})
        return res 

    def finishTask(self,obj_id):
        res=self.db['Tasks'].update_one({"_id":obj_id},{"$set":  {"State": "Done","StopTime":datetime.datetime.now(), "Host":socket.gethostname()}})
        return res

    def NodeTaskDone(self,node_host=socket.gethostname()):
        res=self.db['Nodes'].update_one({"Host":node_host},{"$set":  {"Task":None }})

    def createNode(self,host=socket.gethostname()):
        check=self.get({"Host":host},collection='Nodes')
        if check:
            print("Node already exists")
            return check
        else:
            doc={"Host":host, "Task":None}
            return self.insert(doc,collection='Nodes')

    def TaskToNode(self,task_obj_id,node_host=socket.gethostname()):
        
        res=self.db['Nodes'].update_one({"Host":node_host},{"$set":  {"Task":task_obj_id }})
        return res

    def get_best_eval(self):
        return self.db.Evaluation.find().sort("Score", pymongo.DESCENDING)[0]


    def get_best_eval_prefix(self,prefix,metric="BLEU"):
        return self.db.Evaluation.find({"Model": {"$regex": "^%s" % prefix},"Metric":metric}).sort("Score", pymongo.DESCENDING)[0]


    def get_best_model(self):
        model_name = self.db.Evaluation.find().sort("Score", pymongo.DESCENDING)[0]["Model"]
        return self.db.Models.find({"params.model_name": model_name[2:]})[0]

    def copy_and_change_task(self,task_id,params):#make a copy of a task with new ID and change the parameters specified in params
        task= self.db.Tasks.find_one({"TaskID":task_id})
        task.pop("_id",None)
        task.pop("TaskID",None)
        assert "TaskID" in params
        for key,val in params.iteritems():
            task[key]=val
        self.db.insert(task,"Tasks")

    def copy_and_change_model(self,model_id,params):
        model = self.db.Models.find_one({"ModelID": model_id})
        model.pop("_id", None)
        model.pop("ModelID", None)
        #model.pop("model_name", None)
        assert "ModelID" in params and "model_name" in params
        for key, val in params.iteritems():
            model[key] = val
        self.db.insert(model, "Models")


    #def get_highest_family_id(self):
    #    return max([int(m["ModelID"].split("_")[-2]) for m in self.db.Models.find()])
    
    #def get_family(self,start):
    #    models = self.db.Models.find({"params.model_name": {"$regex": "^%s" % start}})
    #    return models
    def get_highest_family_id(self):
        return self.db.Families.find().sort("FamilyID", pymongo.DESCENDING)[0]
    def get_highest_model_id(self):
        return max(int(self.db.Models.find()["ModelID"].split("_")[-1]))
    def get_highest_task_id(self):
        return self.db.Tasks.find({"TaskID":{"$type":"int"}}).sort("TaskID", pymongo.DESCENDING)[0]["TaskID"]
    def get_lines(self,filename):
        with open(filename) as f:
            for i,l in enumerate(f): pass
        return i
    def get_families(self):
        return self.db.Families.find()
    def get_family_members(self,family_name):
        models = self.db.Models.find({"$or":[{"family": family_name},{"params.family":family_name}]})
        return models

    def get_all_models(self):
        return self.db.Models.find()

    def get_all_tasks(self):
        return self.db.Tasks.find()
    def get_evals(self,model_name):
        return self.db.Evaluation.find({"$or":[{"Model": model_name},{"Model": model_name[2:]}]})

    def get_nbest(self,ValSrc,ValRef,n):
        self.db.Evaluation.create_index('Score')

        models={}
        for e in self.db.Evaluation.find({"ValSrc":ValSrc,"ValRef":ValRef}).sort("Score",pymongo.DESCENDING):
            #print e
            if e["Model"] not in models:
                models[e["Model"]]=e["Score"]
            if len(models)==n:break
        return models
    def get_nbest_in_family(self,ValSrc,ValRef,n,family):
        #self.db.Evaluation.create_index('Score')

        models={}
        for e in self.db.Evaluation.find({"ValSrc":ValSrc,"ValRef":ValRef}).sort("Score",pymongo.DESCENDING):
            #print e
            #print self.get({"params.model_name":e["Model"]},collection="Models")
            if e["Model"] not in models and self.get({"params.model_name":e["Model"]},collection="Models")["params"]["family"]==family:
                models[e["Model"]]=e["Score"]
            if len(models)==n:break
        return models
    def get_best_bleu_of_model(self,model_name):
        return self.get_best_eval_prefix(model_name)["Score"]

    def get_family_evals(self,family, sort="Date"):
        #return self.db.Evaluation.find({"Model": {"$regex": "^\.\/%s" % prefix}}).sort(sort)
        #return self.db.Evaluation.find({"Model": {"family": family}}).sort(sort)
        raise NotImplemented

    def get_params_by_model(self,model_name):
        return self.db.Models.find({"params.model_name": model_name})[0]["params"]
    def get_params_by_eval(self,eval_id):
        model_name = self.db.Evaluation.find({"_id": eval_id})[0]["Model"]
        return self.db.Models.find({"params.model_name": model_name[2:]})[0]["params"]
    def get_best_eval_model_corp(self,model,ValSrc,ValRef,metric="BLEU"):
        return self.db.Evaluation.find({"Model": model,"ValSrc":ValSrc,"ValRef":ValRef}).sort("Score", pymongo.DESCENDING).limit(1)

    def get_nbest_eval_corp(self,n,ValSrc,ValRef,metric="BLEU"):
        return self.db.Evaluation.find({"Metric":metric,"ValSrc":ValSrc,"ValRef":ValRef}).sort("Score", pymongo.DESCENDING).limit(n)


    def get_learning_curves(self,model_name,val_ref=None):

        evals=self.get_evals(model_name).sort("Date")
        #corpora=evals.distinct("ValSrc")
        groupedByCorp={}
        for i,e in enumerate(evals):
            print e["ValRef"]
            print val_ref
            try:
                if val_ref and val_ref!=e["ValRef"]:
                    print e["ValRef"]
                    continue
                if '-'.join((e["ValSrc"],e["ValRef"])) in groupedByCorp:
                    groupedByCorp['-'.join((e["ValSrc"],e["ValRef"]))].append([e["Date"],e["Score"]])
                else:
                    groupedByCorp['-'.join((e["ValSrc"],e["ValRef"]))]=[[e["Date"],e["Score"]]]
            except Exception as e:
                print "Error"
                print e

#        return zip((e["Date"],e["Score"]) for e in evals)
        #return [(e["Date"],e["Score"]) for e in evals]
        print model_name
        return groupedByCorp

    def get_train_start(self, model_name):
            task = self.db.Tasks.find({"Model":model_name}).sort("StartTime")[0]# get the oldest task??
            # corpora=evals.distinct("ValSrc")
            return task["StartTime"]
    def get_train_end(self, model_name):
            task = self.db.Tasks.find({"Model":model_name}).sort("StartTime")[0]# get the oldest task??
            print "END"
            print task
            # corpora=evals.distinct("ValSrc")
            return task["StopTime"]

    def get_highest_corp_id(self):
        try:
            maxi=int(self.db.Corpora.find().sort("CorpID", pymongo.DESCENDING).limit(1)[0]["CorpID"])
            print maxi
        except Exception as e:
            print e
            maxi=0
        return maxi
    def create_corp(self,name,srcPath,refPath,parents=[],desc="",operator=None,direction="encs",type="training"):
        high=self.get_highest_corp_id()
        doc={"CorpID":high+1,"CorpName":name,"Source":srcPath,"Reference":refPath,"Parents":parents,"Description":desc,\
             "Operator":operator,"Direction":direction,"Type":type, "Lines":self.get_lines(srcPath)}
        self.db.Corpora.save(doc)
        return high+1

    def create_family(self,FamilyName="",FamilyID=None):
        self.insert({"FamilyID":FamilyID,"FamilyName":FamilyName},"Families")
    def get_all_tasks(self):
        return self.db.Tasks.find()

    def add_model_to_family(self,family_id,model_params):
        #should check if common params are the same, TODO
        self.db.Families.update({"FamilyID": family_id},
                                {"$addToSet": {"Models": model_params["model_name"]}}, True)

    def get_family(self,model_name):
        try:
            name=self.get({"params.model_name":model_name},collection="Models")["Family"]
        except:
            name=self.get({"params.model_name":model_name},collection="Models")["params"]["family"]

        print name
        return self.get({"FamilyName":name},collection="Families")

    def get_all_corpora(self):
        return self.db.Corpora.find()


    #### Nasledujici funkce slouzi k prevodu databaze ze starsiho schematu, jinak by se nemely nikde pouzivat


    def fix_families(self):
        for m in self.db.Models.find():
            self.db.Models.update_one({"_id":m["_id"]},{"$set":{"family":'_'.join(m["params"]["model_name"].split("_")[:-1])}})

            fam=self.get({"FamilyID":int(m["ModelID"].split("_")[-2])},collection="Families")
            if not fam:
                self.insert({"FamilyID":int(m["ModelID"].split("_")[-2])},"Families")
            self.db.Families.update({"FamilyID":int(m["ModelID"].split("_")[-2])},{"$addToSet":{"Models":m["params"]["model_name"]}},True)
            self.db.Families.update({"FamilyID":int(m["ModelID"].split("_")[-2])}\
                                    ,{"$set":{"FamilyName":'_'.join(m["params"]["model_name"].split("_")[:-1])}}, True)
    def scores_to_float(self):
        evals = self.db.Evaluation.find()
        for e in evals:
            self.db.Evaluation.update_one({"_id": e["_id"]}, {"$set": {"Score": float(e["Score"])}})
    def add_params_to_families(self):
        for f in self.db.Families.find():
            #print f["Models"][0]
            m=self.db.Models.find({"params.model_name":f["Models"][0]}).limit(1)[0]

           # commonList=("encoder",
            f["CommonParams"]={
                "encoder" : m["params"]["encoder"],
                "enc_depth" : m["params"]["enc_depth"],
                "enc_depth_bidirectional" :m["params"]["enc_depth_bidirectional"],
                "decoder" : m["params"]["decoder"],
                "decoder_deep" : m["params"]["decoder_deep"],
                "dec_depth" :m["params"]["dec_depth"],
                "enc_recurrence_transition_depth" : m["params"]["enc_recurrence_transition_depth"],
                "dec_base_recurrence_transition_depth" : m["params"]["dec_base_recurrence_transition_depth"],
                "dec_high_recurrence_transition_depth" : m["params"]["dec_high_recurrence_transition_depth"],
                "dim_word" : m["params"]["dim_word"],
                "dim" : m["params"]["dim"],
                "family":f["FamilyName"]
            }
            self.db.Families.save(f)
    def fix_eval(self):
        self.db.Evaluation.update_many({"ValRef":{"$exists":False}},{"$set":{"ValSrc":"/mnt/nfs//hq.20170623.cs-en.dev.bpe.200.en","ValRef":"/mnt/nfs//hq.20170623.cs-en.dev.bpe.200.cs","Description":"Dev set"}})
    def add_number_of_lines(self):
        for c in self.db.Corpora.find():
            print c
            #print len(open("/home/cepin/JRC-Acquis.en-fr.fr.tcs.train.bpe.shuf").readlines())
            c["Lines"]=self.get_lines(c["Source"])
            #c["Lines"]= len(open(c["Source"]).readlines())

            self.db.Corpora.save(c)
    def add_unique_indices(self):
        self.db.Tasks.create_index('TaskID',unique=True)
        self.db.Models.create_index('params.model_name',unique=True)
        self.db.Models.create_index('ModelID',unique=True)
        self.db.Corpora.create_index('CorpName',unique=True)
        self.db.Corpora.create_index('CorpID',unique=True)
        self.db.Families.create_index('FamilyID',unique=True)
        self.db.Families.create_index('FamilyName',unique=True)
        #self.db.Operators.create_index('OperatorID',unique=True)
        self.db.Operators.create_index('Name',unique=True)
    def add_normal_indices(self):
        self.db.Evaluations.create_index('Model')
        self.db.Evaluations.create_index('Date')
        self.db.Evaluations.create_index('ValRef')
        self.db.Evaluations.create_index('ValSrc')
        self.db.Evaluations.create_index('Score')


    def strip_corp_path(self):
        for c in self.db.Corpora.find():
            c["Source"]=c["Source"].strip()
            c["Reference"]=c["Reference"].strip()
            self.db.Corpora.save(c)
    def fix_model_path_eval(self):
        for e in self.db.Evaluation.find({"Model":{"$regex":"\/mnt\/models\/\/.*"}}):
            e["Model"]=e["Model"].split("/")[-1]
            self.db.Evaluation.save(e)
    def family_to_params(self):
        for m in self.db.Models.find({"family":{"$exists":True}}):
            #m["params"]["family"]=m["family"]
            self.db.Models.update_one({"params.model_name":m["params"]["model_name"]},{"$set": {"params.family":m["family"]}})

    def host_to_port(self,host):
        #d={"micha6f7300001Y":"50040","micha6f73000014":"50030","micha6f73000005":"50023","micha6f7300000L":"50014","micha6f73000020":"50042","micha6f7300000X":"50017","micha6f7300000U":"50002","micha6f73000029":"50046","micha6f7300002A":"50047"}
        d={u'50047': u'micha6f7300002A', u'50059': u'micha6f7300002M', u'50069': u'micha6f73000036', u'50058': u'micha6f7300002L', u'50042': u'micha6f73000020', u'50053': u'micha6f73000030', u'50068': u'micha6f73000035', u'50071': u'micha6f73000038', u'50000': u'micha6f73000002', u'50001': u'micha6f73000001', u'50002': u'micha6f7300000U', u'50003': u'micha6f73000004', u'50004': u'micha6f7300000B', u'50005': u'micha6f7300000C', u'50006': u'micha6f7300000V', u'50007': u'micha6f7300000E', u'50008': u'micha6f7300000F', u'50009': u'micha6f7300000G', u'50052': u'micha6f7300002Z', u'50064': u'micha6f7300002R', u'50066': u'micha6f73000033', u'50043': u'micha6f73000021', u'50028': u'micha6f73000012', u'50029': u'micha6f73000013', u'50048': u'micha6f7300002B', u'50049': u'micha6f7300002C', u'50060': u'micha6f7300002N', u'50061': u'micha6f7300002O', u'50022': u'micha6f73000010', u'50023': u'micha6f73000005', u'50020': u'micha6f7300000R', u'50021': u'micha6f7300000S', u'50026': u'micha6f73000008', u'50027': u'micha6f73000009', u'50024': u'micha6f73000006', u'50025': u'micha6f73000011', u'50062': u'micha6f7300002P', u'50073': u'micha6f7300004C', u'50075': u'micha6f7300004I', u'50072': u'micha6f7300004B', u'50065': u'micha6f73000032', u'50070': u'micha6f73000037', u'50044': u'micha6f73000022', u'50067': u'micha6f73000034', u'50050': u'micha6f7300002X', u'50045': u'micha6f73000028', u'50074': u'micha6f7300004H', u'50046': u'micha6f73000029', u'50063': u'micha6f7300002Q', u'50017': u'micha6f7300000X', u'50016': u'micha6f7300000N', u'50015': u'micha6f7300000M', u'50014': u'micha6f7300000L', u'50013': u'micha6f7300000K', u'50012': u'micha6f7300000W', u'50011': u'micha6f7300000I', u'50010': u'micha6f7300000H', u'50040': u'micha6f7300001Y', u'50019': u'micha6f7300000Z', u'50018': u'micha6f7300000Y', u'50039': u'micha6f7300001D', u'50038': u'micha6f7300001C', u'50051': u'micha6f7300002Y', u'50056': u'micha6f7300002J', u'50057': u'micha6f7300002K', u'50041': u'micha6f7300001Z', u'50055': u'micha6f7300002I', u'50054': u'micha6f73000031', u'50031': u'micha6f73000015', u'50030': u'micha6f73000014', u'50033': u'micha6f73000017', u'50032': u'micha6f73000016', u'50035': u'micha6f73000019', u'50034': u'micha6f73000018', u'50037': u'micha6f7300001B', u'50036': u'micha6f7300001A'}
        return d[host]
    def generate_host_to_port(self):
        host_dict={}
        for m in self.get_all_models():
           # print m
            try:
                host= self.get_model_host(m["params"]["model_name"])
            except:
                print name
                print "host neexistuje"
                continue
            name="%s.best-valid-script.npz"%m["params"]["model_name"]
            print name
            print host
            path="/home/big_maggie/data/models/azure/"
            done = False
            for root, dirs, files in os.walk(path):
                if name in files:

                    p= os.path.join(root, name)
                #    print p
                    #print len(p.split("/"))
                    if len(p.split("/"))==8:
                        if done:
                            print "OMG"
                            return
                        done=True
                        dir=p.split("/")[-2]
                        print dir
                        if dir in host_dict and host_dict[dir]!=host:
                            print "To se mi nelibi"
                            return
                        host_dict[host]=dir
        print host_dict
    def fix_model_names(self):
        regx = re.compile("^\.\/")
        for e in self.db.Evaluation.find({"Model": regx}):
            print e["Model"]
            self.db.Evaluation.update_one({"_id":e["_id"]},{"$set":{"Model":e["Model"][2:]}})
            print e["Model"][2:]
    def fix_val_ref(self):
        for e in self.db.Evaluation.find({"ValRef": {"$exists":False}}):
            self.db.Evaluation.update_one({"_id":e["_id"]},{"$set":{"ValSrc":"/mnt/nfs//hq.20170623.cs-en.dev.bpe.200.en","ValRef":"/mnt/nfs//hq.20170623.cs-en.dev.200.cs"}})

if __name__=="__main__":
    mongo=MongoConn()
    #mongo.add_unique_indices()
    #mongo.add_normal_indices()
    #print mongo.generate_host_to_port()
    #mongo.family_to_params()
    for model in mongo.get_all_models():# in ["model_marian272.npz"]:
    	model_name=model["params"]["model_name"]
        par=model["params"]

       	if "Parents" not in par: 
            print ("no parents")
            continue
       	if par["Parents"][0] not in [u'model_marian76.npz',u'model_marian72.npz',u'model_marian62.npz']:
            print (par["Parents"])
            print (type((par["Parents"])))	
            continue
        with open("evals/filter/%s"%model_name,"w") as f:
            par=model["params"]
            #par=mongo.db.Models.find({"params.model_name": model_name})[0]["params"]   
            print par
            try:
                print par["task_type"]
                typ=par["task_type"]
            except:
                typ=par["Description"]
            try:
                print par["TrainCorp"]
                tc=par["TrainCorp"]
            except:
                tc=par["src_train"]
            try:
                print par["Parents"]
                prn=par["Parents"]
            except:
                prn="None"
    
            f.write("%s\n%s\n%s\n%s\n"%(par["optimizer"],typ,tc,prn))
            print 
            try:
                test=mongo.get_best_eval_model_corp(model_name,"/mnt/nfs/himl.testing.cs-en.tcs.bpe.en","/mnt/nfs/himl.testing.cs-en.tcs.cs",metric="BLEU")[0]
            #print ([t for t in test])
    	        dev=mongo.get_best_eval_model_corp(model_name,"/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe","/mnt/nfs/himl.tuning.cs-en.cs.tcs",metric="BLEU")[0]
		#2017-10-04 02:26:08.741000
            	#diff = datetime.datetime.strptime(dev["Date"], '%Y-%m-%d %H:%M%S.%f') - datetime.datetime.strptime(test["Date"], '%Y-%m-%d %H:%M%S.%f')
		#print (test)
                diff=dev["Date"]-test["Date"]
                #f.write(str(par))
                f.write("BEST:%s\t%s\t%s\n"%(dev["ValRef"],dev["Date"],dev["Score"]))
                f.write("BEST:%s\t%s\t%s\n"%(test["ValRef"],test["Date"],test["Score"]))
                f.write("DIFF:%s\n"%diff)
                if diff.total_seconds() / 60.0>10:
                    f.write("WARNING\n")

            except Exception as e:
                f.write(str(e))
            for e in mongo.get_evals(model_name):
                print (e["ValSrc"])
                f.write("%s\t%s\t%s\n"%(e["ValRef"],e["Date"],e["Score"]))
                print ("%s\t%s\t%s"%(e["ValRef"],e["Date"],e["Score"]))
    exit()
    #mongo.strip_corp_path()
    #mongo.add_number_of_lines()
    #mongo.fix_val_ref()
    #print mongo.host_to_port("micha6f7300000B")
    print mongo.get_nbest("/mnt/nfs/himl.testing.cs-en.tcs.bpe.en","/mnt/nfs/himl.testing.cs-en.tcs.cs",5)
    print mongo.get_nbest("/home/big_maggie/data/models//azure/mnt/nfs/newstest2016-encs-src.en.bpe.noLex.tcs","/home/big_maggie/data/models//azure/mnt/nfs/newstest2016-encs-ref.cs.tok",5)
    print mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs","/mnt/nfs/newstest2016-encs-ref.cs.tok",5)

    #mongo.fix_model_path_eval()
