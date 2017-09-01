import sys
import io
import nltk
import numpy as np
from collections import defaultdict
import cPickle as pickle
import re
"""
Eats a text file with a query per line and outputs subqueries
from the query using ngrams from 2 to 4
"""

def read_sample_file(filename):
    samples = []
    for line in io.open(filename,'r',encoding='utf-8').readlines():
        samples.append(line)
    return samples

def generate_all_subqueries(queries):
    extended_samples = []
    map_query_to_subquery = defaultdict(list)
    head = 0
    for indx, query in enumerate(queries):
        subqueries = generate_subqueries(query)
        extended_samples += subqueries
        map_query_to_subquery[indx] = list(np.arange(head,head+len(subqueries)))
        head = head + len(subqueries)

    return extended_samples, map_query_to_subquery

def generate_subqueries(query):
    subqueries = []
    #tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    query = re.findall("\w+", query, re.U)
    query = ' '.join(query)
    subqueries.append(query)
    for n in np.arange(5,8): # generates up to 4 grams
        ngrams = nltk.ngrams(query.split(),n)
        for grams in ngrams:
            subqueries.append(' '.join(grams))

    return subqueries

def save_queries(sentences, filename):
    text_file = io.open(filename+".txt", "w",encoding='utf-8')
    for query in sentences:
        text_file.write(query+'\n')

if __name__=='__main__':
    samples = read_sample_file(sys.argv[1])
    extended_samples, mapping = generate_all_subqueries(samples)
    pickle.dump(mapping, open('map.pkl','wb'))
    print mapping

    save_queries(extended_samples, sys.argv[2])
