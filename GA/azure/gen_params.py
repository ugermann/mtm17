import random


#tady jsou nejaka rozumna rozmezi hodnot a step
class Ranges:
	##NEMATUS START
	dim_word=(128,512,64)
	dim=(128,1024,64)
	dropout_embedding=(0.0,0.6)#,0.05)
	dropout_hidden=(0.0,0.6)#,0.05)
	dropout_source=(0.0,0.6)#,0.05)
	dropout_target=(0.0,0.6)#,0.05)
#	encoder
	enc_depth=(1,2,1)
	enc_depth_bidirectional=(1,2,1)
#	decoder
#	decoder_deep=
	dec_depth=(1,4,1)
#	dec_deep_context
	enc_recurrence_transition_depth=(1,4,1)
	dec_base_recurrence_transition_depth=(2,4,1)
	dec_high_recurrence_transition_depth=(1,1,1)
	decay_c=(0.01,0.5)#,0.01) #???
	lrate=(0.00001,0.1)#,0.0001) #???
	lrate_decay=(0.1,0.99)
	dec_deep_context=("True","False")
	##NEMATUS END
	
#popis parametru: https://github.com/EdinburghNLP/nematus 	
class Params(Ranges):
	def __init__(self):
		
		
		random.seed()
		self.working_dir="/home/big_maggie/data/models/nematus/models/"
		self.data_dir="/home/big_maggie/data/models/nematus/models/"
		
		self.working_dir="/mnt/nfs/"
		self.data_dir="/mnt/nfs/"
		self.nematus_home="/mnt/nfs/nematus/"
		self.marian_home="/mt/marian/build/"
		self.moses_home="/mt/mosesdecoder/"


		self.model_path="./$model_name"
		
		self.src_train="$data_dir/hq.20170623.cs-en.train.bpe.en.shuf"
		self.tgt_train="$data_dir/hq.20170623.cs-en.train.bpe.cs.shuf"
		
		self.src_val="$data_dir/hq.20170623.cs-en.dev.bpe.200.en"
		self.tgt_val="$data_dir/hq.20170623.cs-en.dev.bpe.200.cs"
		self.tgt_val_post="$data_dir/hq.20170623.cs-en.dev.200.cs"

		self.src_dict="$data_dir/hq.20170623.cs-en.train.bpe.en.json" 
		self.tgt_dict="$data_dir/hq.20170623.cs-en.train.bpe.cs.json"			
                self.src_dict="/mnt/nfs/vocab.en.yml"
                self.tgt_dict="/mnt/nfs/vocab.cs.yml"		
		self.val_script="validate_$model_name.sh"

		self.optimizer="adam"
		
		
	def gen_architecture(self):
		random.seed()
		self.encoder="gru"
		self.enc_depth=random.randrange(*Ranges.enc_depth)
		while True:
			self.enc_depth_bidirectional=random.randrange(*Ranges.enc_depth_bidirectional)
			if self.enc_depth_bidirectional<=self.enc_depth:
				break
		self.decoder="gru_cond"
		self.decoder_deep="gru"
		#self.dec_deep_context=random.choice(Ranges.dec_deep_context)

		self.dec_depth=random.randrange(*Ranges.dec_depth)
	#	dec_deep_context
		self.enc_recurrence_transition_depth=random.randrange(*Ranges.enc_recurrence_transition_depth)
		self.dec_base_recurrence_transition_depth=random.randrange(*Ranges.dec_base_recurrence_transition_depth)
		self.dec_high_recurrence_transition_depth=1#random.randrange(*Ranges.dec_high_recurrence_transition_depth)
		#self.decay_c=random.uniform(*Ranges.decay_c)
		#self.lrate=random.uniform(*Ranges.lrate)
		self.dim_word=random.randrange(*Ranges.dim_word)
		self.dim=random.randrange(*Ranges.dim)
	
	
	def gen_learning_params(self,i):	
		random.seed()
		#self.dropout_embedding=random.uniform(*Ranges.dropout_embedding)
		#self.dropout_hidden=random.uniform(*Ranges.dropout_hidden)
		#self.dropout_source=random.uniform(*Ranges.dropout_source)
		#self.dropout_target=random.uniform(*Ranges.dropout_target)
		#self.decay_c=random.uniform(*Ranges.decay_c)
		#self.lrate=0.01
		if i==0:
			self.dropout_embedding=0.1
			self.dropout_hidden=0.1
			self.dropout_source=0.1
			self.dropout_target=0.1
			self.dropout_target=0.1

			self.decay_c=0.001
			self.lrate=0.0001
			self.lrate_decay=0.99

		else:
			self.dropout_embedding=0.2
			self.dropout_hidden=0.2
			self.dropout_source=0.2
			self.dropout_target=0.2
			self.decay_c=0.1
			self.lrate=0.001
			self.lrate_decay=0

		#self.src_train="$data_dir/rusk.cs.bpe.rusk.shuf"
		#self.tgt_train="$data_dir/rusk.cs.bpe.cs.shuf"
		#self.src_val="$data_dir/secret/top_secret_dev.ru.bpe"
		#self.tgt_val="$data_dir/secret/top_secret_dev.cs.bpe"
		#self.src_dict="$data_dir/rusk.cs.bpe.rusk.json" 
		#self.tgt_dict="$data_dir/rusk.cs.bpe.cs.json"
 

	def dict(self):
		return {attr:value for attr, value in self.__dict__.iteritems()}
	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			yield attr, value

