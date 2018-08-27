import numpy as np
import random

model1 = "/home/big_maggie/data/models/nematus/models/encs.hq/models/model.npz"
model2 = "/home/big_maggie/data/models/nematus/models/encs.hq/models/model.npz.best_bleu"
# model1="/home/big_maggie/data/models/nematus/models/encs.hq/models/model.npz.best_bleu"
models = ["encs.hq/models/model.iter930000.npz", "encs.hq/models/model.iter840000.npz", model1, model2,
          "encs.hq/models/model.iter2440000.npz"]


# np.set_printoptions(threshold=float('inf'))
def load(model):
    # layers={}
    # d=np.load(model)
    # print (np.load(model))
    return {l[0]: l[1] for l in np.load(model).iteritems()}


def average(weights,
            weight_weights=[]):  # list of weights of the same layer from different models (with the same architecture)
    random.seed()
    # weights=[l for l in layers]
    return sum(np.asarray(weights).astype('float32')) / len(weights)


# print (weights)
# return weights[0].astype('float32'))


def diff(weights1, weights2):
    return weights1 - weights2


# model1_layers=load(model1)
# model2_layers=load(model2)
old_layers = [load(m) for m in models]
new_layers = {}

for layer_name in (old_layers[0].keys()):
    # new_layers[layer_name]=average([model1_layers[layer_name],model2_layers[layer_name]])
    new_layers[layer_name] = average([layers[layer_name] for layers in old_layers])
# print average([model1_layers[layer_name],model2_layers[layer_name]])
# print new_layers
np.savez("new_model.npz", **new_layers)
