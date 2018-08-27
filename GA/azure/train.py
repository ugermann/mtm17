import numpy
import os

from nematus.nmt import train

WDIR = "/home/big_maggie/data/models/nematus/models/"

def main(job_id, params):
    print params
    validerr = train(saveto=params['model'][0],
                    reload_=params['reload'][0],
                    dim_word=params['dim_word'][0],
                    dim=params['dim'][0],
                    n_words=params['n-words'][0],
                    n_words_src=params['n-words'][0],
                    decay_c=params['decay-c'][0],
                    clip_c=params['clip-c'][0],
                    lrate=params['learning-rate'][0],
                    optimizer=params['optimizer'][0],
                    maxlen=50,
                    batch_size=80,
                    valid_batch_size=80,
					          datasets=[WDIR + 'hq.20170623.cs-en.train.bpe.en', WDIR + 'hq.20170623.cs-en.train.bpe.cs'],
				          	valid_datasets=[WDIR + 'hq.20170623.cs-en.dev.bpe.en', WDIR + 'hq.20170623.cs-en.dev.bpe.cs'],
			          		dictionaries=[WDIR + 'hq.20170623.cs-en.train.bpe.en.json', WDIR + 'hq.20170623.cs-en.train.bpe.cs.json'],
                    validFreq=20000,
                    dispFreq=20000,
                    saveFreq=40000,
                    sampleFreq=20000,
                    use_dropout=params['use-dropout'][0],
                    overwrite=False,
                    external_validation_script=WDIR + 'validate.sh',
		    objective='MRT'
)
    return validerr

if __name__ == '__main__':
    main(0, {
        'model': [WDIR + 'model.npz'],
        'dim_word': [500],
        'dim': [1024],
        'n-words': [85000],
        'optimizer': ['adadelta'],
        'decay-c': [0.],
        'clip-c': [1.],
        'use-dropout': [False],
        'learning-rate': [0.0001],
        'reload': [True]})

