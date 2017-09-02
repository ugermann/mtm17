OUTNAME = test_out 
for i in {0..100}
do
  cat ../triplets/sample_$i | \
  # preproces
  #moses-scripts/scripts/tokenizer/normalise-punctuation.perl -l de | \
  #moses-scripts/scripts/tokenizer/tokenizer.perl -l de -penn | \
  #moses-scripts/scripts/recases/truecase.perl -model de-en/trucase-model.de |
  #\
  #translate
  marian-dev/build/s2s -m model/baseline/model.npz -v model/baseline/corpus.bpe.de.json model/baseline/corpus.bpe.en.json >> $OUTNAME # |\
  #postprocess
  #moses-scripts/scripts/recaser/detruecase.perl | \
  #moses-scripts/scripts/tokenizer/detokenizer.perl -l en >> test_out-stuff
done

# compute bleu score (error in perl scrip :()
# perl ./moses-scripts/scripts/generic/multi-bleu.perl [target] < [output]
# perl ./moses-scripts/scripts/generic/multi-bleu.perl mtm17/python/data/test_unicode_en.txt < $OUTNAME
