#!/bin/sh

device=cuda0
working_dir=/home/big_maggie/data/models/nematus/models/
dev=$working_dir/corp/hq.20170623.cs-en.dev.bpe.30.en
ref=$working_dir/corp/hq.20170623.cs-en.dev.30.cs
moses_home=/home/big/usr/moses20161024/mosesdecoder/
moses_scripts=/home/big/usr/moses20161024/mosesdecoder/scripts
nematus_home=/home/big_maggie/usr/nematus/
date=`date +"%d_%m_%Y_%H:%M"`
source /home/big_maggie/usr/miniconda/bin/activate
# decode
#$amunn_bin/amunn \
#   -m $prefix.dev.npz -n -d $dev_id --threads 2   \
#	-s $working_dir/corpus.bpe.$src.vocab -t $working_dir/corpus.bpe.$tgt.vocab \
#    < $dev > $dev.output.dev
#export PYTHONPATH=$dl4mt_home
#THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn time python $dl4mt_home/nmt/translate.py \
#   -m $prefix.dev.npz \
#   -i $dev -o $dev.output.dev -k 12 -n -p 2

THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn,profile=True  python $nematus_home/nematus/translate.py \
    -p 4 --models new_model.npz  -i $dev -o $dev.output.dev -k 5 -n  
  

./postprocess.sh < $dev.output.dev > $dev.output.postprocessed.dev

## get BLEU
$moses_scripts/generic/multi-bleu.perl $ref < $dev.output.postprocessed.dev 

#$mydir/nist_heldout.sh >> ${prefix}_nist_bleu_scores
