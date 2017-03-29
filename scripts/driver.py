#!/usr/bin/env python
import logging
import sys

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
import matplotlib.pyplot as plt
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
            200,
            activation="relu",
            input_dim=7,
            init="uniform",
    #        weights=[10*numpy.random.randn(1, 200), 10*numpy.random.randn(200)]
        )
    )
    model.add(Dense(1, init='uniform', activation='sigmoid'))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(
        loss='mean_squared_error',
        optimizer=sgd,
        metrics=['accuracy']
    )

    return model

def main():
    logging.basicConfig(level=logging.INFO)
    dataset_dir = sys.argv[1]

    # 1. Create neural networks
    model = getMLP()
    mlp_network = bpl.BPM(
        width = 10,
        height = 5,
        learningRate = 0.1,
        dataSize = 7
    )

    # 2. Train each neural network
    song_limit = 1
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        logging.info("Retrieved {}".format(w.absoluteName))

        # Features, Samples
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        samples = [
            1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
        ]
        #print samples
        model.fit(
            numpy.array(features),
            numpy.array([
                1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
            ]),
            epochs=100,
            batch_size=30
        )
    
        preds = model.predict(numpy.array(features))
        if i >= song_limit:
            break
        #print preds
        # Train Mike's MLP
        #for i, f in enumerate(features):
        #    print len(f)
        #    mlp_network.iterate(
        #        f,
        #        1.0 if w.isBeat(i * 0.03) else 0.0
        #    )

    # 3. Predict, graph 
    graph_limit = 5
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        preds = model.predict(numpy.array(features))

        plt.figure(1)
        # Waveform amplitudes per feature
        ratio = len(w.waveform) / preds
        plt.plot(
            [ k / w.samplingRate for k in xrange(0, len(waveform)) ],
            w.waveform,
            'b'
        )
        plt.plot(
            [ k * ratio for k in xrange(0, len(features)) ],
            preds
            ,'r'
        )
        plt.savefig('graphs/{}_waveform.png'.format(w.songName))

        plt.figure()
        plt.plot(w.beats, [ 1.0 for w in beats ], 'ro')
        plt.savefig('graphs/{}_beats.png'.format(w.songName))

        if i >= graph_limit:
            break




if __name__ == "__main__":
    main()
