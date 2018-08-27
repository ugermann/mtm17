#!/bin/bash
#echo "Validating..."
device=cuda0
sudo chmod 777 /mnt/
mkdir /mnt/models
[INSERT_SETUP_HERE]

desc_train="$desc""- train set"
desc_dev="$desc""- dev set"
desc_test="$desc""- test set "

train=$src_val_train
train_ref=$tgt_val_train_post

dev=$src_val
dev_ref=$tgt_val_post

test=$src_val_test
test_ref=$tgt_val_test_post

date=`date +"%d_%m_%Y_%H:%M"`


$marian_home/s2s -v $src_dict $tgt_dict -i $dev -m $model_path -b 10 -n 2> valid_err_dev$date.log \
    | sed 's/\@\@ //g' | $moses_home/scripts/recaser/detruecase.perl > output.postprocessed_dev$date

$marian_home/s2s -v $src_dict $tgt_dict -i $test -m $model_path -b 10 -n 2> valid_err_test$date.log \
    | sed 's/\@\@ //g' | $moses_home/scripts/recaser/detruecase.perl > output.postprocessed_test$date

$marian_home/s2s -v $src_dict $tgt_dict -i $train -m $model_path -b 10 -n 2> valid_err_train$date.log \
    | sed 's/\@\@ //g' | $moses_home/scripts/recaser/detruecase.perl > output.postprocessed_train$date

# get BLEU
BLEUDEV=`$moses_home/scripts/generic/multi-bleu.perl $dev_ref < output.postprocessed_dev$date | cut -f 3 -d ' ' | cut -f 1 -d ','`
BLEUTRAIN=`$moses_home/scripts/generic/multi-bleu.perl $train_ref < output.postprocessed_train$date | cut -f 3 -d ' ' | cut -f 1 -d ','`
BLEUTEST=`$moses_home/scripts/generic/multi-bleu.perl $test_ref < output.postprocessed_test$date | cut -f 3 -d ' ' | cut -f 1 -d ','`

echo $BLEUDEV
source /share/michal/env/bin/activate
#python  save_eval.py `basename "$0"` $model_path  $BLEU $date

python  save_eval.py `basename "$0"` $model_name  $BLEUTRAIN $date output.postprocessed_train$date $train  $train_ref "$desc_train"
python  save_eval.py `basename "$0"` $model_name  $BLEUDEV $date output.postprocessed_dev$date $dev  $dev_ref "$desc_dev"
python  save_eval.py `basename "$0"` $model_name  $BLEUTEST $date output.postprocessed_test$date $test  $test_ref "$desc_test"