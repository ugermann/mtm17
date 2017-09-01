import cPickle as pickle
import sys
import io
import os
import numpy as np
import spacy
from spacy.symbols import nsubj, VERB, NOUN, PROPN, ADJ

nlp_de = spacy.load('de')
#nlp_en = spacy.load('en')

def load_mapping(pkl):
    return pickle.load(open(pkl,'rb'))

def load_txt(filepath):
    queries = io.open(filepath,'r',encoding='utf-8').readlines()
    return queries

def compute_relevancy(q1, q2):
    doc1 = nlp_de(q1)
    doc2 = nlp_de(q2)

    structure, maxq1q2 = word_overlap(q1,q2,doc1,doc2)
    morphology = pos_overlap(q1,q2,doc1,doc2,maxq1q2)
    #print 'structure', structure
    #print 'morphology', morphology

    return structure, morphology

def select_relevant_queries(queries, subqueries, subqueries_target, mapping):
    text_file = io.open("best_match_3.txt", "w",encoding='utf-8')
    start = 0
    count = 0
    os.mkdir('triplets')
    for indx, query in enumerate(queries):
        list_to_iter = mapping[indx]
        scores = []
        subqueries_retrieved = []
        subqueries_retrieved_t = []
        for tmp,subquery_indx in enumerate(list_to_iter):
                for subindx in range(5):
                    test_indx = subindx+subquery_indx*5#+start
                    print test_indx
                    struc, morph = compute_relevancy(query, subqueries[test_indx])
                    #if struc > 0.1 or morph > 0.1:
                    #    print 'scores:', struc, morph
                    #    print 'query:', query
                    #    print 'similar query:', subqueries[subquery_indx]

                    score = struc*0.7 + 0.3*morph
                    scores.append(score)
                    subqueries_retrieved.append(subqueries[test_indx])
                    subqueries_retrieved_t.append(subqueries_target[test_indx])
                    #if score_old < score:
                    #    best_match_index = test_indx
                    #    score_old = score

        # get top 3 matches
                start += len(list_to_iter)*5
        sorted_rankings  = sorted(set(zip(scores, subqueries_retrieved, subqueries_retrieved_t)), key = lambda x: x[0], reverse=True)
        text_file.write('query: ' + query+'\n')

        for score, subquery, _ in sorted_rankings[0:5]:
            text_file.write('subquery: '+subquery+'\n')
            text_file.write('score: ' + str(score).decode('utf-8')+'\n')

        write_file(query, sorted_rankings[0:5], indx)
        if count > 10:
            return
        count = count + 1

    text_file.close()

def write_file(query, sorted_l, indx):
    """ writes triplets of files to a designated path"""
    folder = 'triplets/'
    sample = io.open(folder+"sample_"+str(indx), "w",encoding='utf-8')
    sample.write(query)
    source = io.open(folder+"train_source_" + str(indx), "w",encoding='utf-8')
    target = io.open(folder+"train_target_" + str(indx), "w",encoding='utf-8')

    for _, s, t in sorted_l:
        source.write(s)
        target.write(t)

    sample.close()
    source.close()
    target.close()


def word_overlap(q1,q2,doc1,doc2):
    q1 = set(q1.split())
    q2 = set(q2.split())
    pos1 = []
    pos2 = []

    for word1,word2 in zip(doc1,doc2):
        if word1.pos == VERB or word1.pos == NOUN or word1.pos == PROPN or word1.pos == ADJ:
            pos1.append(word1.text)

        if word2.pos == VERB or word2.pos == NOUN or word2.pos == PROPN or word2.pos == ADJ:
            pos2.append(word2.text)

    return len(set(pos1) & set(pos2))/float(np.max([len(set(pos1)),len(set(pos2)),1])), np.max([len(q1),len(q2),1])

def pos_overlap(q1,q2,doc1,doc2,maxq1q2):
    pos1 = []
    pos2 = []
    numerator = 0
    for word1,word2 in zip(doc1,doc2):
        pos1.append(word1.pos)
        pos2.append(word2.pos)
        #
        #if (word1.pos == word2.pos):
        #    numerator =+1

    common = lcs(pos1,pos2)
    score = len(common)/np.max([float(maxq1q2),1])
    #if score > 0.1:
    #    print pos1
    #    print pos2
    #    print q1
    #    print q2

    return score

def lcs(a, b):
    tbl = [[0 for _ in range(len(b) + 1)] for _ in range(len(a) + 1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            tbl[i + 1][j + 1] = tbl[i][j] + 1 if x == y else max(
                tbl[i + 1][j], tbl[i][j + 1])
    res = []
    i, j = len(a), len(b)
    while i and j:
        if tbl[i][j] == tbl[i - 1][j]:
            i -= 1
        elif tbl[i][j] == tbl[i][j - 1]:
            j -= 1
        else:
            res.append(a[i - 1])
            i -= 1
            j -= 1
    return res[::-1]

if __name__=='__main__':
    mapping = load_mapping(sys.argv[1])
    queries = load_txt(sys.argv[2])
    subqueries = load_txt(sys.argv[3])
    subqueries_target = load_txt(sys.argv[4])

    select_relevant_queries(queries, subqueries, subqueries_target, mapping)
