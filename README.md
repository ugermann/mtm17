# Repository for 2017 MT Marathon project on fast adaptation for neural MT

## [Project Wiki](https://github.com/ugermann/mtm17/wiki)

## Existing baseline models 
- [WMT17 models by UEdin (http://data.statmt.org/mtm17/)
  these can be used under the [creative commons non-commercial share-alike license](https://creativecommons.org/licenses/by-nc-sa/3.0/))

## Related repositories:
- [Text indexing with suffix arrays](https://github.com/ugermann/btm)
- [Marian](https://github.com/marian-nmt/marian-dev)

### Installing Marian (Translation only)
```
sudo apt-get update && sudo apt-get install -y \
	cmake \
	git \
	libboost-dev \
	libeigen3-dev \
        libopenblas-base \
        libopenblas-dev \
	python \
	python-dev \
	python-pip \
	gfortran \
	zlib1g-dev \
	g++ \
	automake \
	autoconf \
	libtool \
	libboost-all-dev \
	libgoogle-perftools-dev \
	libpcre3-dev
git clone https://github.com/marian-nmt/marian.git
cd marian
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=release -DCUDA=OFF -DMARIAN=OFF ..
make -j
```
### Installing Marian (Training and translation)

Like above, but replace 
- `https://github.com/marian-nmt/marian.git`
  with
  `https://github.com/marian-nmt/marian-dev.git`

- the `cmake` line with `cmake ..`

### Downloading existing models
For German-to-English, e.g.
```
wget -r -e robots=off -nH -np -R index.html* http://data.statmt.org/mtm17/models/de-en/newest/
```






