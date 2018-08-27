#!/bin/sh

device=cpu
working_dir=/home/big_maggie/data/models/nematus/models/
dev=$working_dir/hq.20170623.cs-en.dev.bpe.200.en
ref=$working_dir/hq.20170623.cs-en.dev.200.cs
prefix=$working_dir/model.npz
moses_home=/home/big/usr/moses20161024/mosesdecoder/
moses_scripts=/home/big/usr/moses20161024/mosesdecoder/scripts
nematus_home=/home/pepa/models/nematus/
date=`date +"%d_%m_%Y_%H:%M"`
# decode
#$amunn_bin/amunn \
#   -m $prefix.dev.npz -n -d $dev_id --threads 2   \
#	-s $working_dir/corpus.bpe.$src.vocab -t $working_dir/corpus.bpe.$tgt.vocab \
#    < $dev > $dev.output.dev
#export PYTHONPATH=$dl4mt_home
#THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn time python $dl4mt_home/nmt/translate.py \
#   -m $prefix.dev.npz \
#   -i $dev -o $dev.output.dev -k 12 -n -p 2

THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn  python $nematus_home/nematus/translate.py \
    -p 4 --models $prefix.dev.npz   -i $dev -o $dev.output.dev -k 5 -n  
  

./postprocess.sh < $dev.output.dev > $dev.output.postprocessed.dev

## get BLEU
BEST=`cat ${prefix}_best_bleu || echo 0`
echo $date  >> ${prefix}_bleu_scores
$moses_scripts/generic/multi-bleu.perl $ref < $dev.output.postprocessed.dev >> ${prefix}_bleu_scores
BLEU=`$moses_scripts/generic/multi-bleu.perl $ref < $dev.output.postprocessed.dev | cut -f 3 -d ' ' | cut -f 1 -d ','`
BETTER=`echo "$BLEU > $BEST" | bc`
cp $dev.output.postprocessed.dev "dev.output.postprocessed.dev$date"
#$mydir/nist_heldout.sh >> ${prefix}_nist_bleu_scores

echo "BLEU = $BLEU"

if [ "$BETTER" = "1" ]; then
  echo "new best; saving"
  echo $BLEU > ${prefix}_best_bleu
  cp ${prefix}.dev.npz ${prefix}.best_bleu
fi
