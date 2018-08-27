#!/usr/bin/env bash
device=cuda0
sudo chmod 777 /mnt/
mkdir /mnt/models
[INSERT_SETUP_HERE]
date=`date +"%d_%m_%Y_%H:%M"`

scp  -oStrictHostKeyChecking=no -v -i /mnt/nfs/azure_key $remote_host:$model_path.best-valid-script.npz $model_path.copy
if [ ! -s $model_path ]; then
    echo "Original model not found!"
    exit 10
fi

$marian_home/s2s -v $src_dict $tgt_dict -i $src_trans -m $model_path.copy -b 10 -n 2> translation_err$date.log \
    | sed 's/\@\@ //g' | $moses_home/scripts/recaser/detruecase.perl > $out_trans

echo "Backtranslation done"
source /mnt/nfs/env/bin/activate
python  save_backcorp.py `basename "$0"` $model_name  $date $out_trans $out_name $orig_corpus $src_trans
