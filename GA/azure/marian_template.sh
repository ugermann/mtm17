#!/bin/bash
echo "Starting training"
#exit
main_dir="."
preallocate=0
marian_home=/mt/marian/build


#chmod +x "$val_script"
device=0
[INSERT_SETUP_HERE]
#model_path=$model_name
$marian_home/marian \
  -m $model_path           \
  --type s2s                       \
  --dim-emb $dim_word                      \
  --dim-rnn $dim                     \
  --enc-cell "$encoder"                    \
  --enc-cell-depth "$enc_recurrence_transition_depth"                \
  --enc-depth "$enc_depth"                     \
  --dec-cell "gru"                     \
  --dec-cell-base-depth "$dec_base_recurrence_transition_depth"           \
  --dec-cell-high-depth "$dec_high_recurrence_transition_depth"            \
  --dec-depth "$dec_depth"                      \
  --skip                                    \
  --layer-normalization                    \
  --best-deep                               \
  --tied-embeddings                         \
  --dropout-rnn "$dropout_hidden"                  \
  --dropout-src "$dropout_source"                    \
  --dropout-trg "$dropout_target"                    \
  -t "$src_train" "$tgt_train"                  \
  --max-length 50                    \
  --disp-freq 1000                  \
  --save-freq 15000                  \
  -d $device                 \
  --dynamic-batching                       \
  -o $optimizer           \
  -l $lrate         \
  --lr-decay $lrate_decay                       \
  --valid-sets "$src_val" "$tgt_val"                           \
  --valid-freq  15000                \
   --valid-metrics "valid-script"     \
  --valid-mini-batch 64              \
  --valid-script-path "$val_script"                   \
  --keep-best                              \
  --valid-log "$val_log" \
  --lr-decay-start 5 1 \
