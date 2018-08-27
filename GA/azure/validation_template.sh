#!/bin/bash

[INSERT_SETUP_HERE]
prefix=$model_paths

dev=$src_val
ref=$tgt_val_post
date=`date +"%d_%m_%Y_%H:%M"`
scp -i /mnt/nfs/azure_key $remote_host:$model_path /mnt/models/$model_name.copy
$marian_home/s2s -v $src_dict $tgt_dict -i $dev -m /mnt/models/$model_name.copy -b 12 -n 2>> valid_err.log \
    | sed 's/\@\@ //g' | $moses_home/scripts/recaser/detruecase.perl > output.postprocessed$date


# get BLEU
BLEU=`$moses_home/scripts/generic/multi-bleu.perl $ref < output.postprocessed$date | cut -f 3 -d ' ' | cut -f 1 -d ','`
echo $BLEU
source /share/michal/env/bin/activate
python  save_eval.py `basename "$0"` $model_path  $BLEU $date output.postprocessed$date $src_val  $tgt_val_post
#rm $model_name
