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
import wavParser


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
    logging.info('Training neural networks')
    song_limit = 5
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        if i >= song_limit:
            break

        logging.info("Retrieved {}".format(w.absoluteName))

        # Features, Samples
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        samples = [
            1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
        ]

        model.fit(
            numpy.array(features),
            numpy.array([
                1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
            ]),
            epochs=100,
            batch_size=30
        )
    
        # Train Mike's MLP
        for i, f in enumerate(features):
            print len(f)
            mlp_network.iterate(
                f,
                1.0 if w.isBeat(i * 0.03) else 0.0
            )

    # 3. Serialize Neural networks
    #model.save('models/keras_mlp.h5')

    # 4. Predict, graph 
    logging.info('Generating predictions and graphs..."')
    graph_limit = 5
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        logging.info('Generating graph for {}'.format(w.songName))
        if i >= graph_limit:
            break
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        preds = model.predict(numpy.array(features))

        # Amplitude graph
        logging.info('Generating waveform graph')
        plt.figure()
        ratio = float(len(w.waveform[0])) / float(len(preds))
        logging.info('{}-{}-{}'.format(len(w.waveform[0]), ratio, w.samplingRate))
        for c in xrange(0, len(w.waveform)):
            plt.plot(
                [ x for x in xrange(0, len(w.waveform[c]), 1000) ],
                [ w.waveform[c][y] for y in xrange(0, len(w.waveform[c]), 1000) ],
            )
        plt.savefig('graphs/{}_waveform.png'.format(w.songName))
       
        # Beats graph
        logging.info('Generating beats graph...')
        plt.figure()
        plt.ylim([0, 2])
#        plt.xlim([0, len(preds)])#w.beats[-1]])

        for b in w.beats:
            print b*w.samplingRate
            plt.axvline(x=b*w.samplingRate, linewidth=0.1, linestyle='solid')

        y = [ p[0] for p in preds ]
        for k in xrange(0, len(preds), 10):
            print k*ratio, preds[k][0]
        print len(w.beats), len(preds)
        plt.plot(
#            [ k / w.samplingRate for 1k in xrange(0, len(preds))],
            [ k * ratio for k in xrange(0, len(preds))],
            [ p[0] for p in preds ],
            'r'
        )

        #plt.plot(w.beats, [ 1.0 for k in w.beats ], 'b')
        plt.savefig('graphs/{}_beats.png'.format(w.songName))
        exit()

        
if __name__ == "__main__":
    main()
