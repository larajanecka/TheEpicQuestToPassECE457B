#!/usr/bin/env python
import logging
import sys

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
import numpy

import bpl
import featureExtractor
import wavutil

def usage():
    print "python driver.py <dataset_directory>"

def getMLP():
    model = Sequential()
    model.add(
        Dense(
            7,
            activation="sigmoid",
            input_dim=1,
            init="uniform",
            weights=[10*numpy.random.randn(1, 200), 10*numpy.random.randn(200)]
        )
    )
    model.add(Dense(output_dim=1, activation='linear', input_dim=200))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(
        loss='mean_squared_error',
        optimizer=sgd,
        metrics=['accuracy']
    )

    return model

def main():
    logging.basicConfig(level=logging.INFO)
    LASDOASD
    dataset_dir = sys.argv[1]

    # Create neural networks
    print 'l'
    model = getMLP()
    mlp_network = bpl.BPM(
        width = 10,
        height = 5,
        learningRate = 0.1,
        dataSize = 7
    )

    # Training
    for w in wavutil.get_wav_files(dataset_dir):
        logging.info("Retrieved {}".format(w.absoluteName))

        # Features, Samples
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        samples = [
            1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
        ]
        print 'lol'
        print samples
        model.fit(
            numpy.array(features),
            numpy.array([
                1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
            ]),
            epochs=1000,
            batch_size=30
        )

        # Train Mike's MLP
        for i, f in enumerate(features):
            print len(f)
            mlp_network.iterate(
                f,
                1.0 if w.isBeat(i * 0.03) else 0.0
            )
