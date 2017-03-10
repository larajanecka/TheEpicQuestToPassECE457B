#!/bin/bash

BALLROOM_DATASET=http://mtg.upf.edu//ismir2004/contest/tempoContest/data1.tar.gz

wget $BALLROOM_DATASET
tar -zxvf data1.tar.gz
