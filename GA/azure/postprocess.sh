#!/bin/sh

#sed -r 's/ \@(\S*?)\@ /\1/g' |
sed -r 's/\@\@ //g' |
#sed "s/&lt;s&gt;//" |
/home/big/usr/moses20161024/mosesdecoder/scripts/recaser/detruecase.perl
