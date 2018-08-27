import fileinput,sys
threshold=float(sys.argv[1])
threshold_oov=0.51 # kolik slov z obou vet musi byt ve slovniku?
min_len=1
filename=sys.argv[2]

with open(filename) as f:
    for line in f.readlines():
        scores=line.split("\t")
        try:
            tok_src=float(scores[2])

            tok_tgt=float(scores[3])
            not_matched_src=float(scores[-3])
            not_matched_tgt=float(scores[-4])
            oov_tgt=float(scores[-1])
            oov_src=float(scores[-2])

        except:
            pass
            #print line
        final_score=(not_matched_src+not_matched_tgt)/(tok_src+tok_tgt)
        oov_score=(oov_src+oov_tgt)/(tok_src+tok_tgt)
        if final_score<=threshold and oov_score<=threshold_oov and tok_src>=min_len and tok_tgt>=min_len:
            print line,
            #print '\t'.join((scores[0],scores[1]))
        #print final_score
