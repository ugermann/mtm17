import nltk

references =open("hq.20170623.cs-en.dev.bpe.half.en.output.postprocessed.dev").readlines()

hypothesis = open("hq.20170623.cs-en.dev.half.cs").readlines()



hypothesis_tokens = [line.split(' ') for line in hypothesis]
references_tokens = [[line.split(' ')] for line in references]


print nltk.translate.bleu_score.corpus_bleu(references_tokens, hypothesis_tokens,smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method4)

