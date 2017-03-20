#!/bin/bash

# ISMIR 2004 Dataset
# Not a good reference because beat annotations are not easy to find
#BALLROOM_DATASET="http://mtg.upf.edu//ismir2004/contest/tempoContest/data1.tar.gz"
#wget $BALLROOM_DATASET
#tar -zxvf data1.tar.gz

# http://www.music-ir.org/mirex/wiki/2012:Audio_Beat_Tracking
# Training set of .wav files and times when beats are intended to occur
#BEATTRACK_DATASET="http://www.music-ir.org/evaluation/MIREX/data/2006/beat/beattrack_train_2006.tgz"
#wget --user beattrack --password b34trx $BEATTRACK_DATASET
#tar -zxvf beattrack_train_2006.tgz

# The Million song dataset
# https://labrosa.ee.columbia.edu/millionsong/pages/getting-dataset#subset
MILLIONSONG_DATASET="http://static.echonest.com/millionsongsubset_full.tar.gz"
wget $MILLIONSONG_DATASET
