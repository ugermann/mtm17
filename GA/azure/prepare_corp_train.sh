corp=$1
src=en
tgt=cs

max_line=80
bpe_merges=89500
working_dir=/home/big_maggie/data/models/nematus/models
bpe_scripts=/home/big_maggie/data/models/nematus/models/subword-nmt
nematus_home=/home/big_maggie/data/models/nematus/models/nematus
#train bpe = subwords, rozsekani neznamych/mene castych slov na mensi jednotky, vyrazne zlepsuje preklad a resi preklad slov, ktera nejsou v trenovacich datech
cat  $working_dir/$corp.$src $working_dir/$corp.$tgt | $bpe_scripts/learn_bpe.py -s $bpe_merges > $working_dir/bpe.model

# apply bpe
$bpe_scripts/apply_bpe.py -c $working_dir/bpe.model < $working_dir/"$corp".$src > $working_dir/"$corp".bpe.$src
$bpe_scripts/apply_bpe.py -c $working_dir/bpe.model < $working_dir/"$corp".$tgt > $working_dir/"$corp".bpe.$tgt

# create dictionaries
python $nematus_home/data/build_dictionary.py $working_dir/"$corp".bpe.$src $working_dir/"$corp".bpe.$tgt

#shuffle
#python shuffle.py $working_dir/"$corp".bpe.$src $working_dir/"$corp".bpe.$tgt

