#!/usr/bin/env python
import logging
import sys

from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, LSTM
from keras.optimizers import SGD
import matplotlib.pyplot as plt
import numpy

import bpl
import featureExtractor
import wavutil
import wavParser


def usage():
    print "python driver.py <dataset_directory> <graph_directory> [ <model_directory> ]"
    print "<dataset-directory> : Directory containing beats, wav files"
    print "<graph_directory> : Where to output generated graphs"
    print "<model_directory> : Where to input neural models from"
    exit(1)

# Generate a MultiLayerPerceptron neural network
# Reasoning
# Layer 1
# - 200 nodes in first layer based on experiment. Yielded better accuracy than 20, 100
# - input_dim : we have 7 features
# - uniform : We do not favour one feature over the other
# Layer 2
# - sigmoid - We need the value to be between [0, 1.0]
# SGD
# - lr of 0.01 : If too high, we skip the optimal weight. If too small, it takes long to converge
# - What that much decay?
#
# - Why that much momentum?
# - Why nesterov momentum and not regular momentum?

def getMLP():
    model = Sequential()
    model.add(
        Dense(
            200,
            activation="relu",
            input_dim=7,
            kernel_initializer="uniform",
        )
    )
    model.add(
        Dense(
            1, 
            kernel_initializer='uniform',
            activation='sigmoid'
        )
    )
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(
        loss='mean_squared_error',
        optimizer=sgd,
        metrics=['accuracy']
    )

    return model

# Generate a recurrent neural network
# TODO
def getRNN():
    model = Sequential()
    model.add(LSTM(4, input_dim=7))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model 

# Train given models. Store them in the model directory
def train_models(keras_models, dataset_dir, model_dir):
    song_limit = 300
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        if i >= song_limit:
            break
        
        logging.info('Starting iteration {}...'.format(i))
        logging.info("Retrieved {}".format(w.absoluteName))

        # Features, Samples
        features, chunk_size = featureExtractor.getFeatures(w.absoluteName)
        samples = [
            1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
        ]
        
        for m in keras_models:
            m[1].fit(
                numpy.array(features),
                numpy.array([
                    1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
                ]),
                epochs=10,
                batch_size=30
            )
    
        # Train Mike's MLP
        #for i, f in enumerate(features):
        #    print len(f)
        #    mlp_network.iterate(
        #        f,
        #        1.0 if w.isBeat(i * 0.03) else 0.0
        #    )
    for m in keras_models:
        m[1].save('{}{}.h5'.format(model_dir, m[0]))

    return keras_models

def main():
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 4:
        usage()

    dataset_dir = sys.argv[1]
    graph_dir = sys.argv[2]

    # 1. Create neural networks
    keras_models = [
        ('keras_MLP', getMLP()),
    ]
    if len(sys.argv) != 4:
        # 2. Train, Serialize each model
        logging.info('Training models...')
        keras_models = train_models(keras_models, dataset_dir, 'models/')
        mlp_network = bpl.BPM(
            width = 10,
            height = 5,
            learningRate = 0.1,
            dataSize = 7
        )
    else:
        logging.info('Loading model from file...')
        keras_models = [
            ('keras_MLP', load_model(sys.argv[3]))
        ]

    # 4. Predict beats, graph 
    logging.info('Generating predictions and graphs..."')
    graph_limit = 300
    for i, w in enumerate(wavutil.get_wav_files(dataset_dir)):
        if i >= graph_limit:
            break
        logging.info('Generating graphs for {}...'.format(w.songName))
        for m in keras_models:    
            features = featureExtractor.getFeatures(w.absoluteName)
            preds = m[1].predict(numpy.array(features))
            loss, accuracy = m[1].evaluate(
                numpy.array(features),
                numpy.array([
                    1.0 if w.isBeat(i * 0.03) else 0.0 for i,f in enumerate(features)
                ]),
            )
            print 'LOSS', loss
            print 'ACCURACY', accuracy
   
            # Generate amplitude graph
            logging.info('Generating waveform graph for \'{}\'...'.format(w.songName))
            plt.figure()
            plt.suptitle('Waveform for \'{}\''.format(w.songName))
            for c in xrange(0, len(w.waveform)):
                plt.plot(
                    [ x for x in xrange(0, len(w.waveform[c]), 1000) ],
                    [ w.waveform[c][y] for y in xrange(0, len(w.waveform[c]), 1000) ],
                )
            plt.savefig('{}{}_waveform.png'.format(graph_dir, m[0] + '-' + w.songName), format='png', dpi=1200)
           
            # Generate Beats graph
            logging.info('Generating beats graph for \'{}\'...'.format(w.songName))
            ratio = float(len(w.waveform[0])) / float(len(preds))
            plt.figure()
            plt.suptitle('{} - Actual vs. Predicted beats for \'{}\''.format(m[0], w.songName))
            plt.ylim([0, 2])
            plt.xlim([w.beats[len(w.beats) / 2]*w.samplingRate , w.beats[-1]*w.samplingRate])
            for b in w.beats:
                plt.axvline(x=b*w.samplingRate, linewidth=0.3, linestyle='solid')

            y = [ p[0] for p in preds ]
            l1, = plt.plot(
                [ k * ratio for k in xrange(0, len(preds))],
                [ p[0] for p in preds ],
                'r',
                linewidth=0.3,
                label='Predicted beats'
            )
            plt.legend(handles=[l1])

            plt.savefig('{}{}_beats.eps'.format(graph_dir, m[0] + '-' + w.songName), format='eps', dpi=1200)

if __name__ == "__main__":
    main()
