import SocketServer
import BaseHTTPServer
import json
import logging, time, re

logging.basicConfig(filename='test.log', level=logging.DEBUG)
import gen_params
from dbutil import MongoConn
import random

# nematus_template=open('nematus_template.sh','r').read()
marian_template = open('marian_template.sh', 'r').read()
marian_template = open('marian_template_second_gen.sh', 'r').read()
marian_template_start_2 = open('marian_template_start_2.sh', 'r').read()

validation_template = open('validate_template.sh', 'r').read()
validation_template = open('validate_template_domain.sh', 'r').read()
back_template = open('backtranslation_template.sh', 'r').read()
eval_template = open('evaluation_template.sh', 'r').read()
# val_template=open('validation_template.sh','r').read()
# val_template=open('val_my.sh','r').read()
# mongo=MongoConn(host="micha6f73000001")
mongo = MongoConn(host="localhost")
from nltk.translate.gleu_score import sentence_gleu


def computeGleu(target, reference):
    return [sentence_gleu([ref], tgt) for (ref, tgt) in zip(reference, target)]


def computeGleuDifference(gleu_src, gleu_tgt):
    return sum([(float(src) - float(tgt)) ** 2 for (src, tgt) in zip(gleu_src, gleu_tgt)])


def expand_vars(params):
    m = None
    for p in params:
        allm = re.findall(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*', str(params[p]))
        allm.sort(key=len)
        allm.reverse()
        for m in allm:  # expand longer matches first, for example enc_depth vs. enc_depth_bidirectional
            if m and str(m)[1:] in params:
                # print "found %s"%str(m)[1:]
                params[p] = params[p].replace(m, str(params[str(m[1:])]))
                # if str(params[p]).find("$%s"%key)!=-1:
                # params[p]=params[p].replace("$%s"%key,str(params[key]))
    return params


def expand_vars_script(params, script):
    allm = re.findall(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*', script)
    allm.sort(key=len)
    allm.reverse()
    for m in allm:
        if m and str(m)[1:] in params:
            script = script.replace(str(m), str(params[str(m)[1:]]))

    return script


def construct_doc(params):
    doc = {"TaskID": params["TaskID"],
           "Type": params["Type"],
           "Model": params["model_name"],
           "State": "Waiting",
           "WaitFor": [],
           "StartTime": [],
           "StopTime": [],
           "Priority": 0,
           "Scripts": {
               "RunScriptsFg": {"train": params["final_script"]},
           # tyto skripty jsou na klientovi spusteny a ceka se na ne
               "RunScriptsBg:": {},  # tyto skripty jsou spusteny, ale neceka se na jejich dokonce
               "SupportScripts": {"val": params["val_script"]}  # tyto skripty jsou jenom zkopirovany a chmod +x
           }

           }
    return doc


# train an initial population, generate n training task with random parameters, parameters are specifiel in gen_params.py
def startPopulation(n):
    highest = 29
    x = highest + 1
    while x <= highest + n:
        paramsC = gen_params.Params()  # generovani parametru, v gen_params.py
        paramsC.gen_architecture()
        for i in xrange(0, 2):
            paramsC.gen_learning_params(i)
            params = paramsC.dict()
            # params["model_name"]="model_nematus%s_%s.npz"%(x,i)
            params["model_name"] = "model_marian%s_%s.npz" % (x, i)

            params["model_id"] = "%s_%s" % (x, i)
            params["Type"] = "StartingPopulationTrain"
            params["TaskID"] = "%s_%s" % (x, i)

            params = expand_vars(params)
            head = '\n'.join(["%s=%s" % (p, v) for p, v in params.iteritems()])
            # params['final_script']=nematus_template.replace('[INSERT_SETUP_HERE]',head)
            params["Scripts"]['RunScriptsFg'] = {"train": marian_template.replace('[INSERT_SETUP_HERE]', head)}

            params["Scripts"]['SupportScripts'] = {"val": validation_template.replace('[INSERT_SETUP_HERE]', head)}

            # params['final_script']=expand_vars_script(params,params['final_script'])
            print params
            mongo.createModel(params)
            mongo.generateTask(construct_doc(params))
        x += 1


def makeNoLexCorp():
    mongo.create_corp("HQNoLexTrain", "/mnt/nfs/hq.20170925.cs-en.NoLex.en.train.bpe.shuf",
                      "/mnt/nfs/hq.20170925.cs-en.NoLex.cs.train.bpe.shuf", parents=[],
                      desc="HQ train corpus without lex data", operator=None, direction="encs", type="training")
    mongo.create_corp("HQNoLexDev", "/mnt/nfs/hq.20170925.cs-en.NoLex.en.dev.bpe.shuf",
                      "/mnt/nfs/hq.20170925.cs-en.NoLex.cs.dev.bpe.shuf", parents=[],
                      desc="HQ dev corpus without lex data", operator=None, direction="encs", type="training")
    mongo.create_corp("HQNoLexDevTok", "/mnt/nfs/hq.20170925.cs-en.NoLex.en.dev.bpe.shuf",
                      "/mnt/nfs/hq.20170925.cs-en.NoLex.cs.dev.shuf", parents=[],
                      desc="HQ corpus without lex data, reference not BPE'd", operator=None, direction="encs",
                      type="training")


def startPopulationNoLex():
    highest = mongo.get_all_models().count()
    highest_task = mongo.get_highest_task_id()
    corpTrain = mongo.get({"CorpName": "HQNoLexTrain"}, collection="Corpora")
    corpVal = mongo.get({"CorpName": "HQNoLexDev"}, collection="Corpora")
    corpValTok = mongo.get({"CorpName": "HQNoLexDevTok"}, collection="Corpora")

    for i, n in enumerate([1, 5, 17, 22, 10]):  # best first gen models
        model_id = highest + i + 1
        task_id = highest_task + i + 1
        params = mongo.get({"ModelID": str(n) + "_0"}, collection="Models")["params"]
        del params["final_script"]
        del params["val_script"]
        print params
        # params["model_name"]="model_nematus%s_%s.npz"%(x,i)
        params["model_name"] = "model_marian%s.npz" % model_id
        params["family"] = mongo.get({"ModelID": str(n) + "_0"}, collection="Models")["family"]

        params["model_id"] = model_id
        params["Type"] = "StartingPopulationTrainNoLex"
        params["src_train"] = corpTrain["Source"]
        params["tgt_train"] = corpTrain["Reference"]
        params["src_dict"] = "/mnt/nfs/vocabNoLex.en.yml"
        params["tgt_dict"] = "/mnt/nfs/vocabNoLex.cs.yml"
        params["src_val"] = corpVal["Source"]
        params["tgt_val"] = corpVal["Reference"]
        params["tgt_val_post"] = corpValTok["Reference"]
        params["Description"] = "\"training a copy of model %s without lex data\"" % n
        params["val_script"] = "val$client_date.sh"
        params["val_log"] = "val$client_date.log"
        params["lrate"] = 0.01
        params["lrate_decay"] = 0.95

        task_params = {}

        task_params["ModelID"] = model_id
        task_params["TaskID"] = task_id
        task_params["Model"] = params["model_name"]
        task_params["Type"] = "StartingPopulationTrainNoLex"
        task_params["Description"] = "\"training a copy of model %s without lex data\"" % n

        task_params["State"] = "Waiting"
        task_params["WaitFor"] = []
        task_params["StopTime"] = None
        task_params["StartTime"] = None
        task_params["Priority"] = 2
        task_params["Host"] = None

        task_params["Scripts"] = {}

        params["model_path"] = '/'.join(("/mnt/models/", params["model_name"]))
        params["moses_home"] = "/mt/mosesdecoder/"
        params["marian_home"] = "/mt/marian/build/"

        params = expand_vars(params)
        head = '\n'.join(["%s=%s" % (p, v) for p, v in params.iteritems()])
        # params['final_script']=nematus_template.replace('[INSERT_SETUP_HERE]',head)
        task_params["Scripts"]['RunScriptsFg'] = {"train": marian_template_start_2.replace('[INSERT_SETUP_HERE]', head)}

        task_params["Scripts"]['SupportScripts'] = {"val": validation_template.replace('[INSERT_SETUP_HERE]', head)}

        # params['final_script']=expand_vars_script(params,params['final_script'])
        print params
        mongo.createModel(params)
        mongo.generateTask(task_params)
        mongo.add_model_to_family(n, params)


def startPopulationCsEn():
    # lex??

    highest = mongo.get_all_models().count()
    highest_task = mongo.get_highest_task_id()
    corpTrain = mongo.get({"CorpName": "HQNoLexTrainReversed"}, collection="Corpora")
    corpVal = mongo.get({"CorpName": "HQNoLexDevReversed"}, collection="Corpora")
    corpValTok = mongo.get({"CorpName": "HQNoLexDevTokReversed"}, collection="Corpora")

    for i, n in enumerate([1, 5, 17, 22, 10]):  # best first gen models
        model_id = highest + i + 1
        task_id = highest_task + i + 1
        params = mongo.get({"ModelID": str(n) + "_0"}, collection="Models")["params"]
        del params["final_script"]
        del params["val_script"]
        print params
        # params["model_name"]="model_nematus%s_%s.npz"%(x,i)
        params["model_name"] = "model_marian%s.npz" % model_id

        params["model_id"] = model_id
        params["Type"] = "StartingPopulationTrainNoLexCsEn"
        params["Scripts"] = {}
        params["src_train"] = corpTrain["Source"]
        params["tgt_train"] = corpTrain["Reference"]
        params["src_dict"] = "/mnt/nfs/vocabNoLex.cs.yml"
        params["tgt_dict"] = "/mnt/nfs/vocabNoLex.en.yml"
        params["src_val"] = corpVal["Source"]
        params["tgt_val"] = corpVal["Reference"]
        params["tgt_val_post"] = corpValTok["Reference"]
        params["Description"] = "\"training a copy of model %s without lex data, on cs-en\"" % n
        params["val_script"] = "val$client_date.sh"
        params["val_log"] = "val$client_date.log"
        params["lrate"] = 0.01
        params["lrate_decay"] = 0.95
        params["TaskID"] = task_id
        mongo.create_family(FamilyName="model_marian%s" % model_id, FamilyID=model_id)
        params["family"] = "model_marian%s" % model_id
        # NE
        task_params = {}

        task_params["ModelID"] = model_id
        task_params["TaskID"] = task_id
        task_params["Model"] = params["model_name"]
        task_params["Type"] = "StartingPopulationTrainNoLexCsEn"
        task_params["Description"] = "\"training a copy of model %s without lex data, on cs-en\"" % n

        task_params["State"] = "Waiting"
        task_params["WaitFor"] = []
        task_params["StopTime"] = None
        task_params["StartTime"] = None
        task_params["Priority"] = 2
        task_params["Host"] = None

        task_params["Scripts"] = {}

        params["model_path"] = '/'.join(("/mnt/models/", params["model_name"]))
        params["moses_home"] = "/mt/mosesdecoder/"
        params["marian_home"] = "/mt/marian/build/"

        params = expand_vars(params)
        head = '\n'.join(["%s=%s" % (p, v) for p, v in params.iteritems()])
        # params['final_script']=nematus_template.replace('[INSERT_SETUP_HERE]',head)
        task_params["Scripts"]['RunScriptsFg'] = {"train": marian_template_start_2.replace('[INSERT_SETUP_HERE]', head)}

        task_params["Scripts"]['SupportScripts'] = {"val": validation_template.replace('[INSERT_SETUP_HERE]', head)}

        # params['final_script']=expand_vars_script(params,params['final_script'])
        print params
        mongo.createModel(params)
        mongo.generateTask(task_params)
        # NE
        mongo.add_model_to_family(model_id, params)
    pass


# makes a copy of the specified model and resumes the training on a new corpus
def makeSecondGen(model_name, corp_name_train, corp_name_val, corp_name_val_tok, corp_name_test,
                  corp_name_train_val_tok):
    model = mongo.get({"params.model_name": model_name}, collection="Models")
    # print mongo.db.Models.find({"params.model_name":model_name})[0]
    corpTrain = mongo.get({"CorpName": corp_name_train}, collection="Corpora")  # training set
    # print corpTrain
    corpVal = mongo.get({"CorpName": corp_name_val}, collection="Corpora")  # dev set with truecased and bpe'd ref
    corpValTok = mongo.get({"CorpName": corp_name_val_tok}, collection="Corpora")  # dev set with with tokenized ref
    corpTrainValTok = mongo.get({"CorpName": corp_name_train_val_tok},
                                collection="Corpora")  # part of training set with with tokenized ref so we can observe overfitting/generalization
    corpTest = mongo.get({"CorpName": corp_name_test}, collection="Corpora")  # test set with target side tokenized
    highest_task = mongo.get_all_tasks().count()
    highest_model = mongo.get_all_models().count()

    # model_params=model["params"]
    family = mongo.get_family(model_name)
    # print family
    model_params = family["CommonParams"]
    # print model_params
    # print model
    model_params["lrate"] = model["params"]["lrate"]
    model_params["lrate_decay"] = 0.9  # model["params"]["lrate_decay"]
    model_params["dropout_source"] = model["params"]["dropout_source"]
    model_params["dropout_hidden"] = model["params"]["dropout_hidden"]
    model_params["dropout_target"] = model["params"]["dropout_target"]
    model_params["optimizer"] = model["params"]["optimizer"]

    model_params["Parents"] = [model_name]
    model_params["model_name"] = "model_marian%s.npz" % (highest_model + 1)
    model_params["model_id"] = highest_model + 1
    model_params["TrainCorp"] = corp_name_train
    model_params["ValCorp"] = corp_name_val

    model_params["src_train"] = corpTrain["Source"]
    model_params["tgt_train"] = corpTrain["Reference"]

    model_params["src_val_train"] = corpTrainValTok["Source"]
    model_params["tgt_val_train_post"] = corpTrainValTok["Reference"]

    model_params["src_val"] = corpVal["Source"]
    model_params["tgt_val"] = corpVal["Reference"]
    model_params["tgt_val_post"] = corpValTok["Reference"]
    model_params["src_dict"] = "/mnt/nfs/vocab.en.yml"
    model_params["tgt_dict"] = "/mnt/nfs/vocab.cs.yml"
    model_params["src_val_test"] = corpTest["Source"]
    model_params["tgt_val_test_post"] = corpTest["Reference"]
    model_params["val_script"] = "val$client_date.sh"
    model_params["val_log"] = "val$client_date.log"
    model_params["Description"] = "\"training second generation of model %s\"" % model_name
    model_params["epochs"] = 3
    model_params["parent_host"] = mongo.get_model_host(model_name)
    model_params["parent_path"] = '/'.join(("/mnt/models/", model_name))
    model_params["model_path"] = '/'.join(("/mnt/models/", model_params["model_name"]))
    model_params["moses_home"] = "/mt/mosesdecoder/"
    model_params["marian_home"] = "/mt/marian/build/"

    task_params = {}

    task_params["ModelID"] = highest_model + 1
    task_params["TaskID"] = highest_task + 1
    task_params["Model"] = "model_marian%s.npz" % (highest_model + 1)
    task_params["Type"] = "SecondGenerationTrain"
    task_params["Description"] = "\"Training second generation with different slices of train corpus\""

    task_params["State"] = "Waiting"
    task_params["WaitFor"] = []
    task_params["StopTime"] = None
    task_params["StartTime"] = None
    task_params["Priority"] = 0
    task_params["Host"] = None

    task_params["Scripts"] = {}

    print model_params

    model_params = expand_vars(model_params)
    head = '\n'.join(["%s=%s" % (p, v) for p, v in model_params.iteritems()])
    # print head
    task_params["Scripts"]['RunScriptsFg'] = {"train": marian_template.replace('[INSERT_SETUP_HERE]', head)}

    task_params["Scripts"]['SupportScripts'] = {"val": validation_template.replace('[INSERT_SETUP_HERE]', head)}

    # print "________________________________________-"
    # print model_params
    # print "________________________________________-"
    # print task_params
    # print "________________________________________-"

    mongo.createModel(model_params)
    mongo.add_model_to_family(family["FamilyID"], model_params)
    mongo.generateTask(task_params)


# make db entries for the new corpora
def makeCorpora():
    parent_id = mongo.create_corp("HQTrain", "/mnt/nfs/hq.20170623.cs-en.train.bpe.en.shuf",
                                  "/mnt/nfs/hq.20170623.cs-en.train.bpe.cs.shuf", parents=[],
                                  desc="train HQ korupus, obsahuje Lex soubory, BPE, tok, tcs")
    for i in xrange(5):
        mongo.create_corp("HQTrainPart%s" % i, "/mnt/nfs/hq.20170623.cs-en.train.bpe.en.shuf.part0%s" % i,
                          "/mnt/nfs/hq.20170623.cs-en.train.bpe.cs.shuf.part0%s" % i,
                          parents=[mongo.get({"CorpID": parent_id}, collection="Corpora")],
                          desc="train HQ korupus %s/6, obsahuje Lex soubory, BPE, tok, tcs" % (i + 1))
        # mongo.create_corp("hq.20170623.cs-en.train.NoLex.bpe.en.shuf.part0%s"%i,"hq.20170623.cs-en.train.NoLex.bpe.cs.shuf.part0%s"%i,parents=[parent_id],desc="HQ korupus %s/6, obsahuje Lex soubory"%(i+1))
    mongo.create_corp("WMT16tcs_tok", "/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",
                      "/mnt/nfs/newstest2016-encs-ref.cs.tok", parents=[],
                      desc="WMT16 test set, zdroj tok, tcs a bpe, referennce jenom tok", type="test")
    mongo.create_corp("HQDev_tcs_tcs", "/mnt/nfs/hq.20170623.cs-en.dev.bpe.en", "/mnt/nfs/hq.20170623.cs-en.dev.bpe.cs",
                      parents=[], desc="dev HQ korupus,tok, tcs a bpe", type="dev")
    mongo.create_corp("HQDev200_tcs_tcs", "/mnt/nfs/hq.20170623.cs-en.dev.bpe.200.en",
                      "/mnt/nfs/hq.20170623.cs-en.dev.bpe.200.cs", parents=[],
                      desc="dev HQ korupus | head 200, tok, tcs a bpe", type="dev")
    mongo.create_corp("HQDev_tcs_tok", "/mnt/nfs/hq.20170623.cs-en.dev.bpe.en", "/mnt/nfs/hq.20170623.cs-en.dev.cs",
                      parents=[], desc="dev HQ korupus zdroj tok, tcs a bpe, reference jenom tok", type="dev")
    mongo.create_corp("HQDTrainDev", "/mnt/nfs/hq.20170623.cs-en.train_dev.bpe.en.shuf",
                      "/mnt/nfs/hq.20170623.cs-en.train_dev.cs.tok", parents=[],
                      desc="300 vet z HQ train, pro sledovani BLEU na trenovacich datechs", type="dev")


# evaluate all models using specified dataset
def validateAll(corpName, task_find_params={}, type="Validation"):
    # models=mongo.get_all_models()
    model_ids = []
    for t in mongo.db.Tasks.find(task_find_params):
        model_ids.append(t["ModelID"])
        print model_ids
    models = mongo.db.Models.find({"ModelID": {"$in": model_ids}})
    corp = mongo.get({"CorpName": corpName}, collection="Corpora")
    highest_task = mongo.get_highest_task_id()
    x = highest_task + 1
    # val_params={}
    # script_params={}
    for model_params in models:
        val_params = {}
        script_params = {}

        # print model["params"]
        val_params["ModelID"] = model_params["ModelID"]
        val_params["Model"] = model_params["params"]["model_name"]

        val_params["Type"] = type
        val_params["TaskID"] = x
        val_params["priority"] = 1
        val_params["State"] = "Waiting"
        val_params["WaitFor"] = []
        val_params["StartTime"] = None
        val_params["StopTime"] = None
        val_params["Description"] = "\"Evaluation on Himl test set with second generation models\""
        script_params["model_path"] = model_params["params"]["model_path"]
        script_params["model_name"] = model_params["params"]["model_name"]
        script_params["remote_host"] = mongo.get_model_host(model_params["params"]["model_name"])
        script_params["src_val"] = corp["Source"]  # "/mnt/nfs/newstest2016-encs-src.en.bpe.tcs"
        script_params["tgt_val_post"] = corp["Reference"]  # "/mnt/nfs/newstest2016-encs-ref.cs.tok"
        script_params["marian_home"] = "/mt/marian/build/"
        script_params["src_dict"] = "/mnt/nfs/vocab.en.yml"
        script_params["tgt_dict"] = "/mnt/nfs/vocab.cs.yml"
        script_params["moses_home"] = "/mt/mosesdecoder/"

        script_params["desc"] = val_params["Description"]

        # val_params["TestSetSrc"]="/mnt/nfs/newstest2016-encs-src.en.bpe.tcs"
        # val_params["TestSetRef"]="mnt/nfs/newstest2016-encs-ref.cs.tcs"
        head = '\n'.join(["%s=%s" % (p, v) for p, v in script_params.iteritems()])
        val_params["Scripts"] = {}
        val_params["Scripts"]['RunScriptsFg'] = {"eval": eval_template.replace('[INSERT_SETUP_HERE]', head)}
        val_params["Scripts"]['RunScriptsBg'] = {}
        val_params["Scripts"]['SupportScripts'] = {}
        print val_params
        mongo.generateTask(val_params)
        x += 1
        # break


def validateSecondGen():
    validateAll("HimlTest", task_find_params={"Type": "SecondGenerationTrain"},
                type="Himl validation of second generation")


# model_name=name of a model to continue the training from
def add_mixed_task(model_name, corpName, corpValName, corpDomainValName, corpDomainValDesegName, corpDomainTestName,
                   type="DomainTrainig2"):
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

    task_params = {}

    task_params["ModelID"] = highest_model + 1
    task_params["TaskID"] = highest_task + 1
    task_params["Model"] = "model_marian%s.npz" % (highest_model + 1)
    task_params["Type"] = type  #
    task_params["Description"] = "\"Continued training of %s with mixed corpus %s\"" % (model_name, corpName)

    task_params["State"] = "Waiting"
    task_params["WaitFor"] = []
    task_params["StopTime"] = None
    task_params["StartTime"] = None
    task_params["Priority"] = 0
    task_params["Host"] = None

    task_params["Scripts"] = {}

    print model_params

    model_params = expand_vars(model_params)
    head = '\n'.join(["%s=%s" % (p, v) for p, v in model_params.iteritems()])
    # print head
    task_params["Scripts"]['RunScriptsFg'] = {"train": marian_template.replace('[INSERT_SETUP_HERE]', head)}

    task_params["Scripts"]['SupportScripts'] = {"val": validation_template.replace('[INSERT_SETUP_HERE]', head)}

    # print "________________________________________-"
    # print model_params
    # print "________________________________________-"
    # print task_params
    # print "________________________________________-"

    mongo.add_model_to_family(family["FamilyID"], model_params)
    mongo.createModel(model_params)
    mongo.generateTask(task_params)


def model_crossover_avg(models, weights=[]):
    if not weights:
        weights = [1 / len(weights) for i in weights]
    models = [mongo.get({"params.model_name": m}) for m in models]


# {corpusName:number of lines to select from each corpus
def mix_corpora(corpora, outcorp):
    parents = []
    with open(outcorp["Source"], "w+") as output_src, open(outcorp["Reference"], "w+") as output_ref:

        for corp, lines in corpora.iteritems():
            c = mongo.get({"CorpName": corp}, collection="Corpora")
            print c["Source"]

            # tohle nejde kvuli pameti:
            # input_src = open(c["Source"], "r").readlines()
            # input_ref = open(c["Reference"], "r").readlines()

            # assert len(input_src)==len(input_ref)
            # we need to read both files sequentially
            input_src = open(c["Source"], "r")
            input_ref = open(c["Reference"], "r")
            if int(lines) == int(c["Lines"]):
                print "Using the whole file"
                # for line in xrange(len(input_src)):
                output_ref.writelines(input_ref)
                output_src.writelines(input_src)
            else:
                samples_i = []
                samples_src = []
                samples_ref = []

                # first sample indices (line numbers) from input_src, sequential reading
                for i, line in enumerate(input_src):
                    if i < lines:
                        samples_i.append(i)
                        # samples_tgt.append(line[0])
                        # samples_src.append(line)

                    elif random.random() < lines * 1. / (i + 1):
                        r = random.randint(0, lines - 1)
                        samples_i[r] = i
                        # samples_src[r]=line

                samples_i = set(samples_i)
                input_src.seek(0)
                # now choose the same lines from reference file
                for i, line in enumerate(input_ref):
                    if i in samples_i:
                        samples_ref.append(line)
                for i, line in enumerate(input_src):
                    # print i
                    if i in samples_i:
                        samples_src.append(line)
                output_src.writelines(samples_src)
                print(len(samples_src))
                output_ref.writelines(samples_ref)

                #  else:
                #     print "Sampling"
                #    for line in xrange(random.sample(xrange(len(input_src)),lines)):# more memory effecient than sampling lines directly
                #       output_src.write(input_src[line])
                #      output_ref.write(input_ref[line])

                # tried=set()
                # if len(lines)==c["Lines"]:
                #    output_src.write('\n'.join(input_src))
                #    output_ref.write('\n'.join(input_ref))

                # for x in xrange(lines):
                #    if x>=c["Lines"]-1: # discard tried if all the lines  were already used
                #        tried=set()
                #    i=random.randint(0,c["Lines"]-1) # get line index
                #    while i in tried: i=random.randint(0,lines-1)
                #    #print i

                #   tried.add(i)
            #    output_src.write(input_src[i])
            #    output_ref.write(input_ref[i])
            parents.append(c["CorpName"])

        ###!!!SHUFFLE!!!###
        output_src.seek(0)
        for i, line in enumerate(output_src): pass

        outcorp["Parents"] = parents
        outcorp["Lines"] = i
        outcorp["CorpID"] = mongo.get_highest_corp_id() + 1

        mongo.db.Corpora.save(outcorp)


# mix the corpora in given ratio,possibly oversampling them to get the correct number of lines
def mix_corpora_over(corpus1, corpus2, ratio1, ratio2, lines, outcorp):
    parents = []
    with open(outcorp["Source"], "w+") as output_src, open(outcorp["Reference"], "w+") as output_ref:

        c1 = mongo.get({"CorpName": corpus1}, collection="Corpora")
        c2 = mongo.get({"CorpName": corpus2}, collection="Corpora")

        input_src1 = open(c1["Source"], "r")
        input_ref1 = open(c1["Reference"], "r")
        input_src2 = open(c2["Source"], "r")
        input_ref2 = open(c2["Reference"], "r")
        lines1 = int(ratio1 * lines)
        lines2 = int(ratio2 * lines)
        samples_i1 = {}
        samples_i2 = {}

        samples_src1 = []
        samples_ref1 = []
        samples_src2 = []
        samples_ref2 = []

        # first sample indices (line numbers) from input_src, sequential reading
        for i, line in enumerate(input_src1): pass
        in1_len = i
        for i, line in enumerate(input_src2): pass
        in2_len = i
        for i in xrange(lines1):
            index = random.randint(0, in1_len)
            if index in samples_i1:
                samples_i1[index] += 1
            else:
                samples_i1[index] = 1

        for i in xrange(lines2):
            index = random.randint(0, in2_len)
            if index in samples_i2:
                samples_i2[index] += 1
            else:
                samples_i2[index] = 1

        input_src1.seek(0)
        input_src2.seek(0)

        for i, line in enumerate(input_src1):
            if i in samples_i1:
                lines = [line for x in xrange(samples_i1[i])]
                output_src.writelines(lines)

        for i, line in enumerate(input_src2):
            if i in samples_i2:
                lines = [line for x in xrange(samples_i2[i])]
                output_src.writelines(lines)

        for i, line in enumerate(input_ref1):
            if i in samples_i1:
                lines = [line for x in xrange(samples_i1[i])]
                output_ref.writelines(lines)

        for i, line in enumerate(input_ref2):
            if i in samples_i2:
                lines = [line for x in xrange(samples_i2[i])]
                output_ref.writelines(lines)

        output_src.seek(0)
        for i, line in enumerate(output_src): pass

        outcorp["Parents"] = [corpus1, corpus2]
        outcorp["Lines"] = i
        outcorp["CorpID"] = mongo.get_highest_corp_id() + 1

        mongo.db.Corpora.save(outcorp)


def create_himl_sets():
    mongo.create_corp("HimlTest", "/mnt/nfs/himl.testing.cs-en.tcs.bpe.en",
                      "/mnt/nfs/himl.testing.cs-en.tcs.cs", parents=[],
                      desc="Himl test set", type="test")
    mongo.create_corp("HimlDevDeseg", "/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe",
                      "/mnt/nfs/himl.tuning.cs-en.cs.tcs", parents=[],
                      desc="Himl dev set without bpe on reference side", type="Dev")
    mongo.create_corp("HimlDev", "/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe",
                      "/mnt/nfs/himl.tuning.cs-en.cs.tcs.bpe", parents=[],
                      desc="Himl dev set", type="Dev")


# mongo.create_corp("UFALMed", "/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe",
#                  "/mnt/nfs/himl.tuning.cs-en.cs.tcs.bpe", parents=[],
#                  desc="Himl dev set", type="Dev")

def run_domain_new():
    for x in xrange(0, 10):
        for mod, score in mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",
                                          "/mnt/nfs/newstest2016-encs-ref.cs.tok", 5).iteritems():
            add_mixed_task(mod, "HQUFALMed_2_0.33_0.%s" % x, "HQDev_tcs_tok", "HimlDev", "HimlDevDeseg", "HimlTest")
            add_mixed_task(mod, "UFALMedFilter_2_0.33_0.%s" % x, "HQDev_tcs_tok", "HimlDev", "HimlDevDeseg", "HimlTest")


def make_mono_corp():
    mongo.create_corp("SynCs", "/mnt/nfs/syn_parsed6m.cs.lex_bpe",
                      None, parents=[],
                      desc="Syn2010 cs mono corpus", type="mono")


def make_reversed_corpora():
    for c in mongo.get_all_corpora():
        if c["Type"] != "mono":
            print c["CorpName"]
            try:
                mongo.create_corp(c["CorpName"] + "Reversed", c["Reference"],
                                  c["Source"], parents=[],
                                  desc=c["Description"] + " - reversed (csen)", type=c["Type"], direction="csen")
            except Exception as e:
                print e


def backtranslate():
    i = 0
    make_mono_corp()
    for mod, score in mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",
                                      "/mnt/nfs/newstest2016-encs-ref.cs.tok", 2).iteritems():
        add_backtranslation_task(mod, "SynCs", "SynEnCs", "/mnt/nfs/syn_parsed6m.cs.lex_bpe")
        i += 1


def add_backtranslation_task(model_name, corp_name, out_corp_name, out_corp_path):
    model = mongo.get({"params.model_name": model_name}, collection="Models")
    corp = mongo.get({"CorpName": corp_name}, collection="Corpora")
    highest_val_id = mongo.get_all_tasks().count()
    x = highest_val_id
    # val_params={}
    # script_params={}
    task_params = {}
    script_params = {}

    # print model["params"]
    task_params["ModelID"] = model["ModelID"]
    task_params["Model"] = model["params"]["model_name"]

    task_params["Type"] = "Backtranslation"
    task_params["TaskID"] = x
    task_params["Priority"] = 2
    task_params["State"] = "Waiting"
    task_params["WaitFor"] = []
    task_params["StartTime"] = None
    task_params["StopTime"] = None
    task_params["Description"] = "\"Backtranslation of CS monodata.\""
    script_params["model_path"] = model["params"]["model_path"]
    script_params["model_name"] = model["params"]["model_name"]
    script_params["remote_host"] = mongo.get_model_host(model["params"]["model_name"])
    script_params["src_trans"] = corp["Source"]
    script_params["out_trans"] = out_corp_path
    script_params["out_name"] = out_corp_name
    script_params["orig_corpus"] = corp_name

    # script_params["tgt_val_post"]=corp["Reference"] #"/mnt/nfs/newstest2016-encs-ref.cs.tok"
    script_params["marian_home"] = "/mt/marian/build/"
    script_params["src_dict"] = "/mnt/nfs/vocab.en.yml"
    script_params["tgt_dict"] = "/mnt/nfs/vocab.cs.yml"
    script_params["moses_home"] = "/mt/mosesdecoder/"
    script_params["task_type"] = "Backtranslation"

    script_params["desc"] = task_params["Description"]

    # task_params["TestSetSrc"]="/mnt/nfs/newstest2016-encs-src.en.bpe.tcs"
    # task_params["TestSetRef"]="mnt/nfs/newstest2016-encs-ref.cs.tcs"
    head = '\n'.join(["%s=%s" % (p, v) for p, v in script_params.iteritems()])
    task_params["Scripts"] = {}
    task_params["Scripts"]['RunScriptsFg'] = {"translate": back_template.replace('[INSERT_SETUP_HERE]', head)}
    task_params["Scripts"]['RunScriptsBg'] = {}
    task_params["Scripts"]['SupportScripts'] = {}
    print task_params
    mongo.generateTask(task_params)
    x += 1
    # break


# puvodni pokus s domenovou adaptaci, byly spatne cesty k puvodnim modelum a trenovani zacinalo od zacatku
def run_domain_bad():
    for x in xrange(0, 10):
        mongo.add_operator({"Name": "dictFilter_2_0.33_0.%s" % x, "Type": "filter",
                            "Description": "Filterinbadg with match threshold  0.%s, oov threshold 0.33 and a minimal sentence length of 2",
                            "Source": open("filter.py").read()})

        mongo.create_corp("UFALMedFilter_2_0.33_0.%s" % x, "/mnt/nfs/ufal_medcorp.en.filter0.%s.en.bpe.tcs" % x,
                          "/mnt/nfs/ufal_medcorp.en.filter0.%s.cs.bpe.tcs" % x,
                          parents=["UFALMed"], operator="dictFilter_2_0.33_0.%s" % x,
                          desc="UFAL medical corpus, filtrovani s match thresholdem  0.%s, oov thresholdem 0.33 a minimalni delkou vety 2" % x,
                          type="training")
        lines = mongo.get({"CorpName": "UFALMedFilter_2_0.33_0.%s" % x}, collection="Corpora")["Lines"]

        mixcorp = {"HQTrain": 1000000 - lines, "UFALMedFilter_2_0.33_0.%s" % x: lines}
        try:
            mongo.add_operator({"Name": "mix%s" % (lines / 1000000.0), "Type": "mix",
                                "Description": "Make a milion lines from both corpora, %s percent is from the second one" % (
                                lines / 1000000.0),
                                "Source": ""})
        except:
            print "Operator already exists"
        mix_corpora(mixcorp,
                    {"CorpName": "HQUFALMed_2_0.33_0.%s" % x, "Source": "/mnt/nfs/HQUFALMed0.%s.en.cln" % x,
                     "Reference": "/mnt/nfs/HQUFALMed0.%s.cs.cln" % x, \
                     "Description": "mix %s lines hq, %s lines ufal with filter %s" % (1000000 - lines, lines, x),
                     "Type": "training", "Operator": "mix%s"})
        for mod, score in mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs",
                                          "/mnt/nfs/newstest2016-encs-ref.cs.tok", 5).iteritems():
            add_mixed_task(mod, "HQUFALMed_2_0.33_0.%s" % x, "HQDev_tcs_tok", "HimlDev", "HimlDevDeseg", "HimlTest")
            add_mixed_task(mod, "UFALMedFilter_2_0.33_0.%s" % x, "HQDev_tcs_tok", "HimlDev", "HimlDevDeseg", "HimlTest")


def run_domain_ratios():
    ##mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs", "/mnt/nfs/newstest2016-encs-ref.cs.tok", 1).iteritems():
    for mod in ("model_marian77.npz", "model_marian72.npz"):
        for ratio in xrange(0, 10, 2):
            ratio1 = ratio * 0.1
            ratio2 = 1 - ratio * 0.1
            lines = 1000000
            for filter in xrange(0, 5):
                try:
                    mix_corpora_over("HQTrain", "UFALMedFilter_2_0.33_0.%s" % filter, ratio1, ratio2, lines,
                                     {"CorpName": "HQUFALMedFilter_2_0.33_0.%s_%s_%s" % (filter, ratio1, ratio2),
                                      "Source": "/mnt/nfs/HQUFALMedFilter_2_0.33_0.%s_%s_%s.en" % (
                                      filter, ratio1, ratio2),
                                      "Reference": "/mnt/nfs/HQUFALMedFilter_2_0.33_0.%s_%s_%s.cs" % (
                                      filter, ratio1, ratio2), \
                                      "Description": "mix %s lines hq, %s lines ufal with filter %s" % (
                                          1000000 * ratio1, 1000000 * ratio2, filter), "Type": "training",
                                      "Operator": "mix"})
                except Exception as e:
                    print e
                add_mixed_task(mod, "HQUFALMedFilter_2_0.33_0.%s_%s_%s" % (filter, ratio1, ratio2), "HQDev_tcs_tok",
                               "HimlDev", "HimlDevDeseg", "HimlTest", type="DomainTrainingRatio")


# validateSecondGen()
# run_domain_new()


run_domain_ratios()
# backtranslate()
# makeNoLexCorp()
# make_reversed_corpora()
# startPopulationCsEn()
# startPopulationNoLex()

exit()
# run_domain_new()
# for mod,score in mongo.get_nbest("/mnt/nfs/newstest2016-encs-src.en.bpe.tcs", "/mnt/nfs/newstest2016-encs-ref.cs.tok", 5).iteritems():
#    print mod
# exit()
# makeCorpora()

# mongo.add_unique_indices()
# mongo.strip_corp_path()
# mongo.add_number_of_lines()
# mongo.add_operator({"Name":"Mix5050","Description":"Mix %s\% from both corpora",})
# mongo.create_corp("Emea", "/mnt/nfs/emea.cs-en.cs.cln",
#                  "/mnt/nfs/emea.cs-en.en.cln", parents=[],
#                  desc="mix 1044694 hq, 1044694 emea", type="dev")

mixcorp = {"HQTrain": 1044694, "Emea": 1044694}

# mongo.create_corp("HQEmea5050", "/home/cepin/GA/mix.src","/home/cepin/GA/mix.ref", parents=["HQTrain","Emea"],
# desc="mix 1044694 hq, 1044694 emea", type="dev")

perc_1 = 50
perc_2 = 50
lines_1 = 1044694
lines_2 = 1044694
# mix_corpora(mixcorp, {"CorpName":"HQEmea%s%s"%(perc_1,perc_2),"Source":"/mnt/nfs/HQEmea%s%s.en.cln"%(perc_1,perc_2),"Reference":"/mnt/nfs/HQEmea%s%s.cs.cln"%(perc_1,perc_2),\
#                      "Description":"mix %s hq, %s emea"%(lines_1,lines_1),"Type":"training"})

exit()

# validateAll()


# makeCorpora()
# makeSecondGen("model_marian8_1.npz","HQTrain","HQDev_tcs_tcs","HQDev_tcs_tok","WMT16tcs_tok","WMT16tcs_tok")

# mongo.fix_families()
# mongo.add_params_to_families()
# makeSecondGen("model_marian8_1.npz","HQTrainPart0","HQDev_tcs_tcs","HQDev_tcs_tok","WMT16tcs_tok","HQDTrainDev")

exit()
for i in xrange(5):
    makeSecondGen("model_marian5_0.npz", "HQTrainPart%s" % i, "HQDev_tcs_tcs", "HQDev_tcs_tok", "WMT16tcs_tok",
                  "HQDTrainDev")
    makeSecondGen("model_marian1_0.npz", "HQTrainPart%s" % i, "HQDev_tcs_tcs", "HQDev_tcs_tok", "WMT16tcs_tok",
                  "HQDTrainDev")
    makeSecondGen("model_marian22_0.npz", "HQTrainPart%s" % i, "HQDev_tcs_tcs", "HQDev_tcs_tok", "WMT16tcs_tok",
                  "HQDTrainDev")
    makeSecondGen("model_marian17_0.npz", "HQTrainPart%s" % i, "HQDev_tcs_tcs", "HQDev_tcs_tok", "WMT16tcs_tok",
                  "HQDTrainDev")
    makeSecondGen("model_marian10_0.npz", "HQTrainPart%s" % i, "HQDev_tcs_tcs", "HQDev_tcs_tok", "WMT16tcs_tok",
                  "HQDTrainDev")



# params=Params()
# with open("setup.sh",'w') as f:
#	for p,v in params:
#		f.write("%s=%s\n"%(p,v))
