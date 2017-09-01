# Repository for 2017 MT Marathon project on fast adaptation for neural MT

**Note:** This project requires an NVIDIA GPU and corresponding cuda libraries

## [Project Wiki](https://github.com/ugermann/mtm17/wiki)

# Setup
```
git clone https://github.com/ugermann/mtm17.git mtm17
cd mtm17
git submodule update --init
make marian
make baseline-model
```

# Can we translate?
```
echo 'das Haus ist blau und Blumen wachsen in der Sonne .' \
| marian-dev/build/s2s \
  -m model/baseline/model.npz \
  -v model/baseline/corpus.bpe.de.json \
     model/baseline/corpus.bpe.en.json 
```

# Pre- and postprocessing

Edit `environment.rc` to reflect your local setup. In your current `bash` shell, run
```
. environment.rc
```
to set some environment variable that this setup relies on.

Pipe text through `scripts/preprocess.sh de` and `scripts/preprocess.sh en`, respectively, to perform
- tokenisation
- truecasing
- byte pair encoding

of data in line with the processing that was used to pre-process the original training data

Similarly `scripts/postprocess.sh {de|en}` converts decoder output back to 'normal' text.

# Stuff below is not up-to-date


### Installing Marian (Translation only)
```
export MTM17_ROOT=/some/path
sudo apt-get update && sudo apt-get install -y cmake git libboost-dev libeigen3-dev libopenblas-base \
        libopenblas-dev python python-dev python-pip gfortran zlib1g-dev g++ automake autoconf \
	libtool libboost-all-dev libgoogle-perftools-dev libpcre3-dev
cd ${MTM17_ROOT}
git clone https://github.com/marian-nmt/marian-dev.git
cd marian-dev
git checkout nematus
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=release ..
make -j
```
### Install other things you need
```
cd ${MTM17_ROOT}
https://github.com/marian-nmt/moses-scripts.git
https://github.com/rsennrich/subword-nmt
```

### Download existing baseline model

## Existing baseline models 
- [WMT17 models by UEdin (http://data.statmt.org/mtm17/models/de-en/20170620/)
  these can be used under the [creative commons non-commercial share-alike license](https://creativecommons.org/licenses/by-nc-sa/3.0/))

```
wget -r -e robots=off -nH -np -R index.html* http://data.statmt.org/mtm17/models/de-en//fs/vali0/www/data.statmt.org/summa/mt/models/de-en/20170620/
```

## Related repositories:
- [Text indexing with suffix arrays](https://github.com/ugermann/btm)
  (Note: we never got around to this)
  

Update: Turns out Marian can't handle the 2017 deep models quite yet, so we'll be using the UEdin Models from WMT16.

### Data we can use to create test and adaptation data sets
- [TED](https://wit3.fbk.eu/mt.php?release=2016-01)

## Setting up Marian on Azure instances
```
cd /mt
git clone http:/github.com/marian-nmt/marian-dev.git
cd marian-dev
git checkout nematus
mkdir build
cmake ..
make -j
```
### Translating with the existing model
```
echo 'das Haus ist blau .' | /mt/marian-dev/build/s2s -c /share/mtm17-ug/s2s-conf.yaml
```




