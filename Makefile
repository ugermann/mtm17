# -*- mode: makefile-gmake; tab-width: 4 -*-

all: baseline-model
MODEL_URL=http://data.statmt.org/germann/mtm17/models/wmt17/de-en

marian: marian-dev/build/s2s

baseline-model: model/baseline/model.npz
baseline-model: model/baseline/corpus.bpe.de.json
baseline-model: model/baseline/corpus.bpe.en.json
baseline-model: model/bpe/vocab.de
baseline-model: model/bpe/vocab.en
baseline-model: model/bpe/deen.bpe
baseline-model: model/truecase/truecase-model.de
baseline-model: model/truecase/truecase-model.en

model/baseline/%: 
	mkdir -p ${@D}
	wget ${MODEL_URL}/$* -qO $@_ && mv $@_ $@

model/bpe/%:
	mkdir -p ${@D}
	wget ${MODEL_URL}/$* -qO $@_ && mv $@_ $@

marian-dev/build/s2s:
	mkdir -p marian-dev/build
	cd marian-dev/build && cmake .. && make -j

TC_MODEL_URL=http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/true.tgz 
model/truecase/truecase-model.en: model/truecase/truecase-model.de
model/truecase/truecase-model.de:
	mkdir -p ${@D}
	cd ${@D} && wget ${TC_MODEL_URL} -qO- | tar xvzf -

