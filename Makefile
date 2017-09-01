# -*- mode: makefile-gmake; tab-width: 4 -*-

all: baseline-model
MODEL_URL=http://data.statmt.org/mtm17/models/de-en/20170620/

baseline-model: model/baseline/model.npz
baseline-model: model/baseline/corpus.bpe.de.json
baseline-model: model/baseline/corpus.bpe.en.json
baseline-model: model/bpe/vocab.de
baseline-model: model/bpe/vocab.en
baseline-model: model/bpe/deen.bpe

model/baseline/%: 
	mkdir -p ${@D}
	cd ${@D} && wget ${MODEL_URL}/$* -qO $@_ && mv $@_ $@

model/bpe/%:
	mkdir -p ${@D}
	cd ${@D} && wget ${MODEL_URL}/$* -qO $@_ && mv $@_ $@

marian-dev/build/s2s:
	mkdir -p marian-dev/build
	cd marian-dev/build && cmake .. && make -j

