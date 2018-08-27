#!/bin/sh
exit
echo "Validating..."
device=cuda0
working_dir=/home/big_maggie/data/models/nematus/models/
dev=$working_dir/corp/hq.20170623.cs-en.dev.bpe.30.en
ref=$working_dir/corp/hq.20170623.cs-en.dev.30.cs
moses_home=/home/big/usr/moses20161024/mosesdecoder/
moses_scripts=/home/big/usr/moses20161024/mosesdecoder/scripts
nematus_home=/home/pepa/models/nematus/
date=`date +"%d_%m_%Y_%H:%M"`
source /home/big_maggie/usr/miniconda/bin/activate

dropout_hidden=0.500290178017
decoder=gru_cond
decay_c=0.0927760547712
dropout_source=0.393673926157
data_dir=/home/big_maggie/data/models/nematus/models/
dropout_embedding=0.296508032271
dec_base_recurrence_transition_depth=4
tgt_dict=$data_dir/rusk.cs.bpe.cs.json
enc_depth_bidirectional=4
src_dict=$data_dir/rusk.cs.bpe.rusk.json
tgt_val=$data_dir/corp/hq.20170623.cs-en.dev.bpe.200.cs
dropout_target=0.465140257741
dec_depth=2
decoder_deep=gru
src_val=$data_dir/corp/hq.20170623.cs-en.dev.bpe.200.en
encoder=gru
dec_high_recurrence_transition_depth=6
lrate=0.0860813584899
tgt_train=$data_dir/rusk.cs.bpe.cs.shuf
src_train=$data_dir/rusk.cs.bpe.rusk.shuf
dim=864
enc_recurrence_transition_depth=7
dim_word=576
enc_depth=5
model_path=$data_dir/encs.hq/models/model.npz

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
    -p 1 --models $model_path  -i $src_val -o output_$date -k 2 -n  
  

./postprocess.sh < output_$date > output_$date.postprocessed

## get BLEU
$moses_scripts/generic/multi-bleu.perl $tgt_val < output_$date.postprocessed | cut -f 3 -d ' ' | cut -f 1 -d ','

#$mydir/nist_heldout.sh >> ${prefix}_nist_bleu_scores
