#!/usr/bin/env python

from dbutil import MongoConn
import numpy as np
import pickle
import nltk
import codecs
import random
mongo=MongoConn(host="localhost")

from nltk.translate.gleu_score import sentence_gleu,corpus_gleu
from nltk.translate.bleu_score import sentence_bleu,corpus_bleu

def computeGleu(target,reference):
    return [sentence_gleu([ref.strip()],tgt.strip()) for (ref,tgt) in zip(reference,target)]

def computeGleuDifference(gleu_src,gleu_tgt):
    return sum([(float(src)-float(tgt))**2 for (src,tgt) in zip(gleu_src,gleu_tgt)])/len(gleu_src)

def computeCorpGleu(target,reference):
    return corpus_gleu(reference,target)

def computeCorpBleu(target,reference):
    return corpus_bleu(reference,target)#,smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method7)#,emulate_multibleu=True,smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method5)

def average_models(models,outpath):
    average = dict()
    #models=[models[0]]
    n = len(models)
    print n
    for filename in models:
        print("Loading {}".format(filename))
        with open(filename, "rb") as mfile:
            m = np.load(mfile)
            for k in m:
                if "special" in k:
                    average[k]=m[k]
                #print k
                if k != "history_errsk":
                    # Initialize the key.
                    if k not in average:
                        average[k] = m[k]#*1.01#(((random.random()-.5)/100)+1)
                    # Add to the appropriate value.
                    elif average[k].shape == m[k].shape and "special" not in k:
                        average[k] += m[k]#*1.01#(((random.random()-.5)/100)+1)

                    #print average[k]
                    if  "special" not in k and "emb" not in k:
                        #print k
                        #print type(average[k])
                        #print average[k].shape
                        #rand_mat=0.9+np.random.random_sample(average[k].shape).astype(dtype="float32")*0.2
                        rand_mat=1+np.random.random_sample(average[k].shape).astype(dtype="float32")*0

                        #print rand_mat
                       # print rand_mat.shape

                        old=average[k]
                        average[k]=np.multiply(average[k],rand_mat)
                        if not np.array_equal(old,average[k]):
                            pass
                        #    print "zrada"
                        #print old.dtype
                        #print average[k].dtype
                        #exit()
                        #average[k]=np.multiply(average[k],random.random(.9,1.1))

                    #print (average[k])
                    #exit()
    # Actual averaging.
    for k in average:
        if "special" not in k:
            average[k] /= n


    # Save averaged model to file.
    print("Saving to {}".format(outpath))
    np.savez(outpath, **average)
    return
    model = mongo.get({"params.model_name": model_name}, collection="Models")
    corp = mongo.get({"CorpName": corpName}, collection="Corpora")
    corpDomainVal = mongo.get({"CorpName": corpDomainValName}, collection="Corpora")
    corpDomainValDeseg = mongo.get({"CorpName": corpDomainValDesegName}, collection="Corpora")
    corpVal = mongo.get({"CorpName": corpValName}, collection="Corpora")
    corpDomainTest = mongo.get({"CorpName": corpDomainTestName}, collection="Corpora")

    highest_task = mongo.get_highest_task_id()
    print highest_task
    highest_model = mongo.get_all_models().count()

    # model_params=model["params"]
    family = mongo.get_family(model_name)
    # print family
    model_params = family["CommonParams"]
    print corpName
    # print model_params
    # print model
    model_params["lrate"] = model["params"]["lrate"]
    model_params["lrate_decay"] = 0.9  # model["params"]["lrate_decay"]
    model_params["dropout_source"] = model["params"]["dropout_source"]
    model_params["dropout_hidden"] = model["params"]["dropout_hidden"]
    model_params["dropout_target"] = model["params"]["dropout_target"]
    model_params["optimizer"] = "sgd"  # model["params"]["optimizer"]

    model_params["Parents"] = [model_name]
    model_params["model_name"] = "model_marian%s.npz" % (highest_model + 1)
    model_params["model_id"] = highest_model + 1
    model_params["TrainCorp"] = corpName
    model_params["ValCorp"] = corpDomainValName  # model["ValCorp"]

    model_params["src_train"] = corp["Source"]
    model_params["tgt_train"] = corp["Reference"]

    # model_params["src_val_train"]=corpTrainValTok["Source"]
    # model_params["tgt_val_train_post"]=corpTrainValTok["Reference"]

    model_params["src_val_out"] = corpVal["Source"]
    model_params["tgt_val_out"] = corpVal["Reference"]

    model_params["src_val"] = corpDomainVal["Source"]
    model_params["tgt_val"] = corpDomainVal["Reference"]
    model_params["tgt_val_post"] = corpDomainValDeseg["Reference"]

    model_params["src_dict"] = model["params"]["src_dict"]
    model_params["tgt_dict"] = model["params"]["tgt_dict"]

    model_params["src_val_test"] = model["params"]["src_val_test"]
    model_params["tgt_val_test_post"] = model["params"]["tgt_val_test_post"]

    model_params["src_val_test_domain"] = corpDomainTest["Source"]
    model_params["tgt_val_test_post_domain"] = corpDomainTest["Reference"]

    model_params["val_script"] = "val$client_date.sh"
    model_params["val_log"] = "val$client_date.log"
    model_params["Description"] = "\"domain adaptated version of model %s\"" % model_name
    model_params["epochs"] = 0
    model_params["parent_host"] = mongo.get_model_host(model_name)
    model_params["parent_path"] = '/'.join(("/mnt/models/", model_name))
    model_params["model_path"] = '/'.join(("/mnt/models/", model_params["model_name"]))
    model_params["moses_home"] = "/mt/mosesdecoder/"
    model_params["marian_home"] = "/mt/marian/build/"
    model_params["marian_home"] = "/mt/marian/build/"
    model_params["task_type"] = "DomainTraining2"

import operator
x = mongo.get_nbest_in_family("/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe","/mnt/nfs/himl.tuning.cs-en.cs.tcs",30,"model_marian1")
sorted_x = sorted(x.items(), key=operator.itemgetter(1))
print(sorted_x)

model1=mongo.get({"params.model_name":"model_marian318.npz"},collection="Models")
print model1
model2=mongo.get({"params.model_name":"model_marian216.npz"},collection="Models")
#model3=mongo.get({"params.model_name":"model_marian317.npz"},collection="Models")
model4=mongo.get({"params.model_name":"model_marian208.npz"},collection="Models")
model5=mongo.get({"params.model_name":"model_marian212.npz"},collection="Models")
average_models(["/home/big_maggie/data/models/azure/%s/%s.best-valid-script.npz"%(mongo.host_to_port(mongo.get_model_host(model2["params"]["model_name"])),model2["params"]["model_name"]),\
#"/home/big_maggie/data/models/azure/%s/%s.best-valid-script.npz"%(mongo.host_to_port(mongo.get_model_host(model1["params"]["model_name"])),model1["params"]["model_name"]), \
    #"/home/big_maggie/data/models/azure/%s/%s.best-valid-script.npz"%(mongo.host_to_port(mongo.get_model_host(model3["params"]["model_name"])),model3["params"]["model_name"]),\
        "/home/big_maggie/data/models/azure/%s/%s.best-valid-script.npz"%(mongo.host_to_port(mongo.get_model_host(model4["params"]["model_name"])),model4["params"]["model_name"]),\
        "/home/big_maggie/data/models/azure/%s/%s.best-valid-script.npz"%(mongo.host_to_port(mongo.get_model_host(model5["params"]["model_name"])),model5["params"]["model_name"])
    ],"test.npz")
exit()
print(mongo.get_nbest_in_family("/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe","/mnt/nfs/himl.tuning.cs-en.cs.tcs",30,"model_marian1"))
eval1=mongo.get_best_eval_model_corp(model="model_marian70.npz",ValSrc="/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",ValRef="/mnt/nfs/newstest2016-encs-ref.cs.tok",metric="BLEU")

eval2=mongo.get_best_eval_model_corp(model="model_marian77.npz",ValSrc="/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",ValRef="/mnt/nfs/newstest2016-encs-ref.cs.tok",metric="BLEU")
diff_dict={}
eval_dict={}
out=open("diff_1_himl.tuning.txt","w")
out_bin=open("diff_1_himl.tuning.pickle","wb")

for i,(model,score) in enumerate(mongo.get_nbest_in_family("/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe","/mnt/nfs/himl.tuning.cs-en.cs.tcs",30,"model_marian1").iteritems()):#mongo.get_family_members("model_marian1")):
    #print m
    m=mongo.get({"params.model_name":model},collection="Models")
    print m["params"]["model_name"]
    print i
    try:
        e=mongo.get_best_eval_model_corp(model=m["params"]["model_name"], ValSrc="/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe",
                                   ValRef="/mnt/nfs/himl.tuning.cs-en.cs.tcs", metric="BLEU")
        eval_dict[m["params"]["model_name"]] = e

        #exit()

        #print target


        #print(computeCorpBleu(target, reference))
        #print e["Score"]
        #print nltk.translate.bleu_score.corpus_bleu(reference, target,
         #                                       smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method5)

    except Exception as e:
        print m["params"]["model_name"]
        print e

for model,e in eval_dict.iteritems():
    diff_dict[model]={}
    print model
    target = [sent.strip().split(' ') for sent in e["Output"].split('\n') if sent != '']
    reference = [[sent.strip().split(' ')] for sent in codecs.open(e["ValRef"], "r", "utf-8").readlines() if sent != '']
    print len(target)
    print len(reference)
    try:
        print(computeCorpBleu(target,reference))
    except Exception as e:
        print e
        print target
        print reference
        continue

    gleu1=computeGleu(e["Output"].split('\n'),codecs.open(e["ValRef"], "r", "utf-8").readlines())
    for model2,eval2 in eval_dict.iteritems():
        if model2 not in diff_dict:
            print model,model2
            #print eval2
           # print eval2["Output"]
            gleu2=computeGleu(eval2["Output"].split('\n'),codecs.open(e["ValRef"], "r", "utf-8").readlines())
            diff=computeGleuDifference(gleu1,gleu2)
            print e["Score"],eval2["Score"]

            print diff
            print
            diff_dict[model][model2]=diff


out.write(str(diff_dict))
pickle.dump(diff_dict,out_bin)
model1=mongo.get({"params.model_name":"model_marian213.npz"},collection="Models")
model2=mongo.get({"params.model_name":"model_marian212.npz"},collection="Models")
average_models(["/home/big_maggie/data/models/azure/%s/%s"%(mongo.get_model_host(model1["params.model_name"]),model1["params.model_name"]), \
    "/home/big_maggie/data/models/azure/%s/%s"%(mongo.get_model_host(model2["params.model_name"]),model2["params.model_name"])],"~/test.npz")
#print len(eval1["Output"].split('\n'))

#print len(eval1["Output"].split('\n'))
#print len(open("/mnt/nfs/hq.20170623.cs-en.train_dev.cs.tok").read().split('\n'))
#print(computeCorpBleu(eval1["Output"],open("/mnt/nfs/hq.20170623.cs-en.train_dev.cs.tok").read()))
#print(computeCorpBleu(eval2["Output"],open("/mnt/nfs/hq.20170623.cs-en.train_dev.cs.tok").read()))

#print(computeGleuDifference(gleu1,gleu2))
