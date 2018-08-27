#!/bin/bash
echo "Starting training"
#exit 0
main_dir="."
preallocate=0
#nematus_home=/home/big_maggie/usr/nematus/

#data_dir=/home/big_maggie/data/models/nematus/models/rusk_cs/corp
#working_dir=$main_dir/models
#
#src_train=$data_dir/rusk.cs.bpe.rusk.shuf
#tgt_train=$data_dir/rusk.cs.bpe.cs.shuf 
#src_val=$data_dir/secret/top_secret_dev.ru.bpe
#tgt_val=$data_dir/secret/top_secret_dev.cs.bpe
#src_dict=$data_dir/rusk.cs.bpe.rusk.json 
#tgt_dict=$data_dir/rusk.cs.bpe.cs.json





device=gpu0
#source /home/big_maggie/usr/miniconda/bin/activate

[INSERT_SETUP_HERE]
source /share/michal/env/bin/activate
deactivate
#echo "Starting training with parameters: " 
THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device /usr/bin/python $nematus_home/nematus/nmt.py \
    --model "$model_path" \
    --datasets "$src_train" "$tgt_train" \
    --valid_datasets "$src_val" "$tgt_val"  \
    --dictionaries  "$src_dict" "$tgt_dict" \
    --external_validation_script "$val_script" \
    --reload \
    --batch_size 50 \
    --valid_batch_size 40 \
    --validFreq 1000 \
    --dispFreq 1000 \
    --saveFreq 30000 \
    --sampleFreq 10000 \
    --dim_word "$dim_word" \
	--dim $dim  	 \
	--use_dropout  	 \
	--dropout_embedding "$dropout_embedding"  	 \
	--dropout_hidden "$dropout_hidden"  	 \
	--dropout_source "$dropout_source"  	 \
	--dropout_target "$dropout_target"  	 \
	--layer_normalisation  	 \
	--tie_decoder_embeddings  	 \
	--encoder  $encoder 	 \
	--enc_depth  "$enc_depth"  	 \
	--enc_depth_bidirectional "$enc_depth_bidirectional"    \
	--decoder $decoder  	 \
	--decoder_deep "$decoder_deep"  	 \
	--dec_depth "$dec_depth"  	 \
	--enc_recurrence_transition_depth "$enc_recurrence_transition_depth"  	 \
	--dec_base_recurrence_transition_depth "$dec_base_recurrence_transition_depth"  	 \
	--dec_high_recurrence_transition_depth "$dec_high_recurrence_transition_depth"  	 \
	--decay_c "$decay_c"  	 \
	--lrate "$lrate" 	 \
	--patience 3 	\
	--anneal_restarts 10 	\
	--anneal_decay 0.66 	\
	--optimizer $optimizer
	
	#--tie_encoder_decoder_embeddings  	 \ #musi byt stejny src i tgt dict
	#--dec_deep_context $dec_deep_context  	 \
	#--weight_normalisation  	 \
