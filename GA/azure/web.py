from gen_client import MongoConn
import pymongo
import matplotlib.dates as mdates
import numpy as np
from matplotlib.font_manager import FontProperties
from Tkinter import *
from functools import partial
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from bson import json_util
import matplotlib
import matplotlib.pyplot as plt
from flask import render_template, jsonify,request
from flask import Flask
#from __future__ import print_function
from collections import  OrderedDict
import mpld3
from mpld3 import plugins, utils
import datetime
app = Flask(__name__)

client = MongoConn()

fontP = FontProperties()
fontP.set_size('x-large')
@app.route('/plot_and_info/<model_name>')
def plot_and_info(model_name):
    print model_name
    model=client.get({"params.model_name":model_name},collection="Models")
    fig, ax = plt.subplots(figsize=(12,7))
    h = []
    params = model["params"]
    model_name = params["model_name"]
    #print model_name
    curves = client.get_learning_curves("./" + model_name)#,val_ref="/mnt/nfs/himl.testing.cs-en.tcs.cs")
    #startTime=client.get_train_start(model_name)
    try:
        endTime = client.get_train_end(model_name)
    except:
        endTime=None
    #print curves
    for name,points in curves.iteritems():
        #print points
        #print name
        #print points[0][0]
        #print endTime
        if endTime:
            if points[0][0]>endTime: # aby evaluace po konce trenovani byly zarovnane s koncovym casem
                points[0][0]=endTime
                #print "HA"
        curve = [((date - points[0][0]).total_seconds() / 3600.0, score) for date, score in points]

        c = np.asarray(curve)
        #print c
        # print c
        # fig.autofmt_xdate()
        # max_idx=np.argmax(c[:,1])
        # ax.annotate("test", xy=(c[0],c[1]), xytext=(0, 0),arrowprops=dict(arrowstyle="->"))
        lines = plt.plot(c[:, 0], c[:, 1], marker='o',label=' '.join((model_name, str(max(c[:, 1]))," (",name.split("/")[-1],")")))
        print lines
        mpld3.plugins.connect(fig, mpld3.plugins.PointLabelTooltip(lines[0], labels=c[:, 1].tolist()))
        h.append(lines[0])
    plt.legend(handles=h, loc='lower right', prop=fontP)  # ,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # ax.legend(loc='upper center', bbox_to_anchor=(0.0, -0.05),
    #          fancybox=True, shadow=True)
	
    plt.xlabel('Hours')
    plt.ylabel('BLEU')
    plt.ylim([-5,50])
    plt.title("Learning curves")
    #plugins.connect(fig, plugins.LineLabelTooltip(lines, c[:, 1].tolist()))
    #mpld3.show()
    #plt.savefig("fig.png")
    try:
        params.pop("final_script")
        params.pop("val_script")
    except:
        pass
    try:
        prev_model=client.db.Models.find({'_id': {'$lt': model["_id"]}}).sort([('_id', -1)]).limit(1)[0]["params"]["model_name"]
    except:
        prev_model="asd"
    try:
        next_model=client.db.Models.find({'_id': {'$gt': model["_id"]}}).sort([('_id', 1)]).limit(1)[0]["params"]["model_name"]
    except:
        next_model="asd"

    figure=mpld3.fig_to_html(fig)
    #print figure
    print prev_model
    #params=json.dumps(params, indent=4, sort_keys=True)
    with app.app_context():
        return render_template('model_template.html',  prev_model=prev_model, next_model=next_model,model_name=model_name,figure=figure, params=model["params"])#"<br>".join(["%s:\t%s"%(key, value) for key, value in params.iteritems()]))

@app.route('/plot/<models>')
def plot(models):
    fig, ax = plt.subplots(figsize=(12,7))
    h = []
    h = []
    models=models.split("+")
    models_params={}
    i=0

    for model_name in models:
        i+=1

        # print model_name
        models_params[model_name]='\n'.join(["%s:\t%s"%(key, val) for key,val in client.get({"params.model_name":model_name},collection="Models")["params"].iteritems()])

        curves = client.get_learning_curves("" + model_name,val_ref="/mnt/nfs/himl.testing.cs-en.tcs.cs")
        # startTime=client.get_train_start(model_name)
       # endTime = client.get_train_end(model_name)
        #print curves
        for name, points in curves.iteritems():
            if i==2:
                p=[datetime.datetime(2017, 10, 2, 12, 15, 40, 27000), 21.56]
            else: p=[datetime.datetime(2017, 10, 5, 0, 19, 58, 20000), 21.56]
            points=points[:13]
            points.insert(0,p)
            print points
            # print name
            #print points[0][0]
            endTime=None
            #print endTime

            if endTime:
                if points[0][0] > endTime:  # aby evaluace po konce trenovani byly zarovnane s koncovym casem
                    #points[0][0] = endTime
                    print "HA"
            curve = [((date - points[0][0]).total_seconds() / 3600.0, score) for date, score in points]

            c = np.asarray(curve)
            # print c
            # print c
            # fig.autofmt_xdate()
            # max_idx=np.argmax(c[:,1])
            # ax.annotate("test", xy=(c[0],c[1]), xytext=(0, 0),arrowprops=dict(arrowstyle="->"))
            if i==2: name="Adam"
            else: name="SGD"
            p, = plt.plot(c[:, 0], c[:, 1], marker='o',
                          label=name)
            #p, = plt.plot(c[:, 0], c[:, 1], marker='o',
            #              label=' '.join((model_name, str(max(c[:, 1])), " (", name.split("/")[-1], ")")))
            h.append(p)
    plt.legend(handles=h, loc=3, prop=fontP)  # ,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # ax.legend(loc='upper center', bbox_to_anchor=(0.0, -0.05),
    #          fancybox=True, shadow=True)


    plt.xlabel('Hours')
    plt.ylabel('BLEU')
    #plt.ylim([-5,50])
    plt.ylim([19,24])
    font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 22}
    #matplotlib.rc('xtick', labelsize=50)
    #matplotlib.rc('ytick', labelsize=50)
    matplotlib.rc('font', **font)
    #plt.rc('legend', fontsize=25)

    plt.title("Learning curves")
    plt.savefig("fig.png")

    #mpld3.show()

    try:
        models_params.pop("final_script")
        models_params.pop("val_script")
    except:
        pass

    figure=mpld3.fig_to_html(fig)
    #print figure
    #params=json.dumps(params, indent=4, sort_keys=True)
    #if type(models)!=list: models=[models]
    with app.app_context():
        #print models
        return render_template('plot_models.html', figure=figure, models=models_params)
    # xfmt = mdates.DateFormatter('%d-%m %H:%M')
    # ax.xaxis.set_major_formatter(xfmt)


@app.route('/tasks')
def tasks():
    type_tasks={}
    for task in client.get_all_tasks():
        if "Type" in task:
            type=task["Type"]
        else: type="None"
        if type in type_tasks:
            type_tasks[type].append(task)
        else:
            type_tasks[type]=[task]
    return render_template('tasks.html', type_tasks=type_tasks)

@app.route('/task/<taskID>')
def task(taskID):
    task=client.get({"TaskID":int(taskID)},collection="Tasks")
    print task
    print taskID
    params_pretty='\n'.join(["%s:\t%s" % (key, val) for key, val in task.iteritems()])
    return render_template('task.html', params=task, params_pretty=params_pretty)

if __name__ == "__main__":
    url_for('static', filename='style.css')
    app.run()

@app.route('/models')
def models(filter={},sort="/mnt/nfs/himl.tuning.cs-en.cs.tcs"):
    model_names={model["params"]["model_name"] for model in client.db.Models.find(filter)}
    pipeline = [{"$match": {"ValRef": "/mnt/nfs/himl.tuning.cs-en.cs.tcs"}},
                {"$group": {"_id": "$Model", "Score": {"$max": "$Score"}}}, {"$sort": {"Score": pymongo.DESCENDING}}]
    #models={}
    models=[]
    done=[]
    for e in client.db.Evaluation.aggregate(pipeline):
        print e
        if e["_id"] not in done and e["_id"] in model_names:
#            models.append(client.get({"params.model_name":e["Model"]},collection="Models"))
            models.append(e["_id"])

            done.append(e["_id"])
            #models[e["Model"]] = e["Score"]

    #for m in client.db.Models.find(filter):
    #    try:
    #        best=client.get_best_eval_model_corp(model=m["params"]["model_name"], ValSrc="/mnt/nfs/himl.tuning.cs-en.en.tcs.bpe",
    #                                       ValRef="/mnt/nfs/himl.tuning.cs-en.cs.tcs", metric="BLEU").next()["Score"]
    #    except:
    #        best=0
    #    models.append((best,m))
    #    print best
    #models.sort(key=lambda tup:tup[0])
    #models=[m[1] for m in models]
    return render_template('models.html', models=models, val=client.db.Evaluation.distinct("ValRef"))
@app.route('/models/<param>/<value>')
def filtered_models(param,value):
    try:
        value=int(value)
    except:
        pass
    return models({param:value})

@app.route("/getSortedModels", methods=['GET','POST'])
def getSortedModels():
    ValRef = request.args.get('ValRef')
    pipeline = [{"$match": {"ValRef": ValRef}},
                {"$group": {"_id": "$Model", "Score": {"$max": "$Score"}}}, {"$sort": {"Score": pymongo.DESCENDING}}]
    models = []
    model_names = {model["params"]["model_name"] for model in client.db.Models.find()}
    for e in client.db.Evaluation.aggregate(pipeline):
        print e
        if e["_id"] not in models and e["_id"] in model_names:
            models.append(e["_id"])

            #models.append(client.get({"params.model_name": e["Model"]}, collection="Models"))
    print jsonify({ "models":models })
    return jsonify({ "models":models })

@app.route("/children/<parent>")
def children(parent):
    return models({"params.Parents":{"$in":[parent]}})

plot("model_marian272.npz")
