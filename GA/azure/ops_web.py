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
import matplotlib.pyplot as plt, mpld3
from flask import render_template
from flask import Flask
#from __future__ import print_function

app = Flask(__name__)

class Application(Frame):

    def plot_all(self):
        for button in self.buttons: button.config(relief=RAISED)
        m=self.models

        self.models=[]
        self.plot(m)

    def push(self,button,model):
        print model
        print client.get_model_host(model[2:])
        if model in self.models:
            self.models.remove(model)
            button.config(relief=RAISED)
        else:
            button.config(relief=SUNKEN)

            self.models.append(model)
    def import_params(self,params,text_widget,event):
        text_widget.delete(1.0, END)
        try:
            params.pop("final_script")
            params.pop("val_script")
        except:
            pass
        text_widget.insert(END, json.dumps(params,indent=4, sort_keys=True))
        #add final_script_template_filename and val_script_template_filename to params of each model
        # def rebuild_final
        #def rebuild_val -- znovu vygenerovani sh skriptu po upravach promennych

    def new_task(self):
        top=Toplevel()
        text=Text(top)
        text.pack(side=LEFT)#grid(row=0,column=0,rowspan=2)
        frame = Frame(top)
        scrollbar = Scrollbar(frame, orient=VERTICAL)
        listbox = Listbox(frame, yscrollcommand=scrollbar.set)
        for model in client.get_all_models():
            l=Label(listbox, text=model["params"]["model_name"])
            l.bind("<Double-Button-1>",partial(self.import_params,model["params"],text))
            l.pack()
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        frame.pack(side=RIGHT)
       # scrollbar.pack(side=RIGHT)#.grid(sticky=N+S)
       # listbox.pack()#grid(row=0,column=1, sticky=N+S+E+W)

        b = Button(frame, text="Save", padx=5, pady=5)
        b.pack()#.grid(row=1,column=1)
        #frame.pack(side=RIGHT)#grid(row=0,column=1)




    def show_params(self,params,event):
        top=Toplevel()
        text=Text(top,height=30)
        try:
            params.pop("final_script")
            params.pop("val_script")
        except:
            pass
        text.insert(END, json.dumps(params,indent=4, sort_keys=True, default=json_util.default))

        text.grid(row=0,column=0,rowspan=2)

    def createWidgets(self):
        menubar = Menu(root)
        menubar.add_command(label="Models", command=self.modelFrame.tkraise)
        menubar.add_command(label="Tasks", command=self.taskFrame.tkraise)
        menubar.add_command(label="Evaluations", command=self.evalFrame.tkraise)
        menubar.add_command(label="Corpora", command=self.corpFrame.tkraise)
        menubar.add_command(label="Trees", command=self.treeFrame.tkraise)

        self.master.config(menu=menubar)
        self.taskWidgets()

        self.modelWidgets()
        self.corpWidgets()
        self.treeWidgets()

        self.evalWidgets()
        self.modelFrame.tkraise()
        self.grid()


    def taskWidgets(self):
        #self.frame.__init__(self, self.master)
        #menubar = Menu(root)
        #menubar.add_command(label="Models", command=self.modelWidgets)
        #self.master.config(menu=menubar)
        print "Tasks"
        self.taskFrame.grid(row=0, column=0, sticky='news')

        done_fr = LabelFrame(self.taskFrame, text="Done", padx=10, pady=10)
        pending_fr = LabelFrame(self.taskFrame, text="Pending",  padx=10, pady=10)
        wait_fr = LabelFrame(self.taskFrame, text="Waiting", padx=10, pady=10)
        done_fr.grid(row=0,column=0)
        pending_fr.grid(row=0,column=1)
        wait_fr.grid(row=0,column=2)

        tasks = list(client.get_all_tasks())

        for i,task in enumerate([t for t in tasks if t["State"]=="Done"]):
            print task
            try:
                b = Button(done_fr, text=task["TaskID"], padx=5, pady=5,  bg="#b4ff9b")

                b.config(command=partial(self.task_info,  task))
                b.grid(column=i/10, row=i%10,sticky='news')
                self.buttons.append(b)
            except KeyError:
                print "KeyError"
            #b.bind("<Button-3>", partial(plot_and_info, model))


        for i, task in enumerate([t for t in tasks if t["State"] == "Pending"]):
            try:
                print task

                b = Button(pending_fr, text=task["TaskID"], padx=5, pady=5, bg="#ffc68e")
                b.config(command=partial(self.task_info,  task))
                b.grid(column=i / 10, row=i % 10,sticky='news')
                # b.bind("<Button-3>", partial(plot_and_info, model))

                self.buttons.append(b)
            except KeyError:
                print "KeyError"
        for i, task in enumerate([t for t in tasks if t["State"] == "Waiting"]):
            try:
                print task
                b = Button(wait_fr, text=task["TaskID"], padx=5, pady=5,bg="#5eccff")
                b.config(command=partial(self.task_info,  task))
                b.grid(column=i / 10, row=i % 10, sticky='news')

                self.buttons.append(b)
            except KeyError:
                print "KeyError"
    def evalWidgets(self):
        self.evalFrame.grid(row=0, column=0, sticky='news')


    def modelWidgets(self):
        row=0
        next_b=Button(self.modelFrame, text="Next")
        next_b.grid(row=0, column=0)
        for col,fam in enumerate(families):
            if col%4==0: row+=1
            #print fam
            fr=LabelFrame(self.modelFrame,text=fam["FamilyName"],padx=10,pady=10)
            for c, model in enumerate(client.get_family_members(fam["FamilyName"])):
                #print model
                b=Button(fr, text=model["ModelID"],padx=5,pady=5)
                b.config(command=partial(self.push,b,"./"+model["params"]["model_name"]))
                b.config(font=("Arial","6"))

                b.grid(column=c%20, row=c/20)
                b.bind("<Button-3>",partial(self.plot_and_info,model))

                self.buttons.append(b)
            fr.grid(column=col%4, row=row)
            self.families_frames.append(fr)


        self.plot_b = Button(self.modelFrame)
        self.plot_b["text"] = "Plot",
        self.plot_b["command"] = self.plot_all

        self.plot_b.grid()
        self.modelFrame.grid(row=0, column=0, sticky='news')

    def corpWidgets(self):
        row=0

        for col,corp in enumerate(client.get_all_corpora()):
            if col%4==0: row+=1
            #print model
            b=Button(self.corpFrame, text=corp["CorpName"],padx=5,pady=5)
            b.config(command=partial(self.push_corp,b,corp["_id"]))
            b.grid(column=col%4, row=col/4,sticky='news')
            b.bind("<Button-3>",partial(self.show_corp,corp["_id"]))

            self.buttons.append(b)
        self.mix_b = Button(self.corpFrame)
        self.mix_b["text"] = "Mix",
        self.mix_b["command"] = self.mix_corpora

        self.mix_b.grid()
        self.corpFrame.grid(row=0, column=0, sticky='news')

    def treeWidgets(self):
        c=Canvas(self.treeFrame)
        c.grid(row=0, column=0, sticky='news')
        Label(c,text="Tady bude tree").grid()
        f=Frame(self.treeFrame)
        Label(f,text="A Tady budou evaluace a tak").grid()
        f.grid(row=0, column=1, sticky='news')
        self.treeFrame.grid(row=0, column=0, sticky='news')

    def mix_corpora(self):
        for button in self.buttons: button.config(relief=RAISED)
        c=self.corpora

        self.corpora=[]
        self.mix(c)
    def mix(self,c):
        totalLinesVar=IntVar()
        def lines_to_perc(corp,*args):
            print lines_dict[corp].get()/totalLinesVar.get()
        top = Toplevel(root)
        lines_dict={}
        for col,corp in enumerate(c):
            linesVar=IntVar()
            linesVar.trace('w',partial(lines_to_perc,corp))
            lines_dict[corp]=linesVar
            corpus = client.get({"_id": corp},collection="Corpora")

            fr=LabelFrame(top,text=corpus["CorpName"],padx=10,pady=10)
            for key,value in corpus.iteritems():
                Label(fr,anchor=W, justify="left",text="%s:\t%s"%(key,str(value).strip())).grid(sticky='news')

            lines=Scale(fr,variable=linesVar,to=corpus["Lines"],label=str(linesVar.get()*corpus["Lines"]),orient="horizontal")
            lines.grid(sticky='news')
            lines_label=Label(fr,textvariable=linesVar)
            lines_label.grid()
            fr.grid(column=col%4, row=0,sticky='news')

        total_lines=Spinbox(top,textvariable=totalLinesVar)
        total_lines.delete(0,END)

        total_lines.insert(END,2)
        total_lines.grid(sticky='news')
        do=Button(top,text="Do")
        def pr(arg):
            for k,v in arg.iteritems():
                print k,": ",v.get()
        do.config(command=partial(pr, lines_dict))

        do.grid(sticky='news')
    def push_corp(self,button,objId):

        if objId in self.corpora:
            self.corpora.remove(objId)
            button.config(relief=RAISED)
        else:
            button.config(relief=SUNKEN)

            self.corpora.append(objId)

    def show_corp(self,objId,event):
        top = Toplevel(root)

        text = Text(top, height=30)
        # task.pop("_id")
        corp = client.get({"_id":objId }, collection="Corpora")

        text.insert(END, json.dumps(corp, indent=4, sort_keys=True, default=json_util.default))
        # print model
        text.grid(row=0, column=0, rowspan=1, columnspan=3)
        button = Button(master=top, text='Quit', command=sys.exit)
        button.grid(row=1, column=2, sticky=W + E)

    def task_info(self, task):
        top = Toplevel(root)


        text = Text(top, height=30)
        try:
            task.pop("Script")
            task.pop("ValidationScript")
        except:
            pass
        #task.pop("_id")
        text.insert(END, json.dumps(task, indent=4, sort_keys=True, default=json_util.default))
        model=client.get({"params.model_name":task["Model"]},collection="Models")
        #print model
        text.grid(row=0, column=0, rowspan=1,columnspan=3)
        button = Button(master=top, text='Quit', command=sys.exit)
        button.grid(row=1, column=2,sticky=W+E)
        button = Button(master=top, text='Copy task', command=partial(copy_task, task))
        button.grid(row=1, column=1,sticky=W+E)
        button = Button(master=top, text='Model', command=partial(self.plot_and_info, model))
        button.grid(row=1, column=0,sticky=W+E)

    def plot_and_info(self, model, event=None):
        def onpick(evnt):
            print "test"
        top = Toplevel(root)
        fig, ax = plt.subplots(1)
        h = []
        params = model["params"]
        model_name = params["model_name"]
        #print model_name
        curves = client.get_learning_curves("./" + model_name)#,val_ref="/mnt/nfs/himl.testing.cs-en.tcs.cs")
        #startTime=client.get_train_start(model_name)
        endTime = client.get_train_end(model_name)
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
            p, = plt.plot(c[:, 0], c[:, 1], marker='o',label=' '.join((model_name, str(max(c[:, 1]))," (",name.split("/")[-1],")")))
            h.append(p)
        plt.legend(handles=h, loc='lower right', prop=fontP)  # ,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        # ax.legend(loc='upper center', bbox_to_anchor=(0.0, -0.05),
        #          fancybox=True, shadow=True)
        plt.xlabel('Hours')
        plt.ylabel('BLEU')
        plt.ylim([-5,50])
        plt.title("Learning curves")

        canvas = FigureCanvasTkAgg(fig, master=top)

        canvas.mpl_connect('pick_event', onpick)
        canvas.show()
        #mpld3.show()
        canvas.get_tk_widget().grid()

        canvas._tkcanvas.grid()
        text = Text(top, height=30)
        try:
            params.pop("final_script")
            params.pop("val_script")
        except:
            pass
        text.insert(END, json.dumps(params, indent=4, sort_keys=True))

        text.grid(row=0, column=1, rowspan=2,sticky='news')
        button = Button(master=top, text='Quit', command=sys.exit)
        button.grid(row=1, column=0, sticky='news')
        button = Button(master=top, text='Copy model', command=partial(copy_model, model))
        button.grid(row=1, column=1, sticky='news')
        figure=mpld3.fig_to_html(fig)
        print figure
        params=json.dumps(params, indent=4, sort_keys=True)
        with app.app_context():
            return render_template('model_template.html', model_name=model_name,figure=figure, params=params)

    def plot(self,models):
        # top=Toplevel(root)
        #print models
        fig, ax = plt.subplots(1)
        h = []
        h = []
        for model_name in models:
            # print model_name
            curves = client.get_learning_curves("" + model_name, val_ref="/mnt/nfs/himl.testing.cs-en.tcs.cs")
            # startTime=client.get_train_start(model_name)
           # endTime = client.get_train_end(model_name)
            #print curves
            for name, points in curves.iteritems():
                # print points
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
                p, = plt.plot(c[:, 0], c[:, 1], marker='o',
                              label=' '.join((model_name, str(max(c[:, 1])), " (", name.split("/")[-1], ")")))
                h.append(p)
        plt.legend(handles=h, loc=3, prop=fontP)  # ,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        # ax.legend(loc='upper center', bbox_to_anchor=(0.0, -0.05),
        #          fancybox=True, shadow=True)
        plt.ylim([-5,50])

        plt.xlabel('Hours')
        plt.ylabel('BLEU')
        plt.title("Learning curves")

        # xfmt = mdates.DateFormatter('%d-%m %H:%M')
        # ax.xaxis.set_major_formatter(xfmt)

        plt.show()

        # canvas = FigureCanvasTkAgg(fig, master=top)
        # canvas.show()
        # canvas.get_tk_widget().grid()

    #    canvas._tkcanvas.grid()


    def __init__(self, master=None):


        self.frame=Frame
        self.frame.__init__(self, master)
        self.corpora=[]
        self.buttons=[]
        self.models=[]
        self.families_frames=[]
        self.master=master
        self.treeFrame=Frame(master)
        self.modelFrame=Frame(master)
        self.taskFrame=Frame(master)
        self.evalFrame=Frame(master)
        self.corpFrame=Frame(master)
        #self.corpFrame=Frame(master)

        self.createWidgets()
client = MongoConn("localhost")
#client.fix_families()
#client.scores_to_float()
families=client.get_families()
client.fix_eval()
fontP = FontProperties()
fontP.set_size('small')
models = ["./model_marian8_0.npz", "./model_marian8_1.npz", "./model_marian4_0.npz", "./model_marian3_0.npz",
          "./model_marian1_1.npz"]




def copy_model(model):
    top = Toplevel()
    text = Text(top)
    text.pack(side=LEFT)  # grid(row=0,column=0,rowspan=2)

    # scrollbar.pack(side=RIGHT)#.grid(sticky=N+S)
    # listbox.pack()#grid(row=0,column=1, sticky=N+S+E+W)
    mtext=model
    mtext.pop("_id")
    text.insert(END, json.dumps(mtext, indent=4, sort_keys=True,default=json_util.default))

    b = Button(top, text="Save", padx=5, pady=5)
    b.pack()
    # .grid(row=1,column=1)
    # frame.pack(side=RIGHT)#grid(row=0,column=1)
def copy_task(task):
    top = Toplevel()
    text = Text(top)
    text.pack(side=LEFT)  # grid(row=0,column=0,rowspan=2)

    # scrollbar.pack(side=RIGHT)#.grid(sticky=N+S)
    # listbox.pack()#grid(row=0,column=1, sticky=N+S+E+W)
    ttext=task
    ttext.pop("_id")
    text.insert(END, json.dumps(ttext, indent=4, sort_keys=True,default=json_util.default))

    b = Button(top, text="Save", padx=5, pady=5)
    b.pack()
    # .grid(row=1,column=1)
    # frame.pack(side=RIGHT)#grid(row=0,column=1)





root = Tk()
app = Application(master=root)

root.mainloop()
#root.destroy()

print client.get_best_bleu_of_model("./model_marian3_0.npz")
