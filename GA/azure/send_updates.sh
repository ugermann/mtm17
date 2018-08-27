#!/bin/bash
wget -q -O /dev/null 'http://brno.lingea.cz/alarm/?To='"`whoami`"'%40lingea.cz&From=backup%40brno.lingea.cz&Subject=Nematus%20update&body='"`tail -n 50 /home/big_maggie/data/models/nematus/models/rusk_cs/logs/train.3.log `"

wget -q -O /dev/null 'http://brno.lingea.cz/alarm/?To='"`whoami`"'%40lingea.cz&From=backup%40brno.lingea.cz&Subject=Nematus%20update&body='"`tail -n 50 /home/big_maggie/data/models/nematus/models/rusk_cs/logs/bleu_scores ` "

