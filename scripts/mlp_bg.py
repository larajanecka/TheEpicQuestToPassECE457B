import logging
import mirex
from sklearn.neural_network import MLPClassifier

import wavParser as wav

# This program uses a multilayer perceptron in an attempt to identify beats in songs
# The feature used from audio files are the aggregate of the amplitudes of multiple
# channels per unit time

# Functions used to aggregate amplitudes for multiple channels

# Sum the amplitudes per unit time
def summation(channels):
    result = []
    for i in xrange(0, len(channels[0])):
        result.append(sum([c[i] for c in channels]))
    return result

# Sum the squares of all amplitudes per unit time
def summationSquared(channels):
    result = []
    for i in xrange(0, len(channels[0])):
        result.append(sum([c[i]**2 for c in channels]))
    return result

# Given a WAV file and its aggregate waveform, make training input
def get_training_input(wav_file, aggregate_waveform):
    inputs = []
    for i in xrange(0, len(aggregate_waveform), 1000):
        time = float(i) / wav_file.samplingRate
        is_beat = 0.0
        if "{0:.3f}".format(time) in wav_file.beats:
            is_beat = 1.0
        inputs.append((aggregate_waveform[i:i+1000], is_beat))

    return inputs            

def main():
    logging.basicConfig(level=logging.INFO)

    # Retrieve Wav files, Generate training set
    logging.info("Retrieving dataset...")
    wavfiles = mirex.get_mirex_wav_files("datasets/train")
    logging.info("Retrieved {} wav files".format(len(wavfiles)))

    features = []
    samples = []
    for w in wavfiles:
        logging.info("Aggregating channels for {}".format(w.absoluteName))
        k = summationSquared(w.waveform)
        t = get_training_input(w, k)
        for j in t:
            # Each feature needs the same number entries in its array
            # The final feature extracted from a WAV file may be shorter, thus remove it
            if len(j[0]) == 1000:
                features.append(j[0])
                samples.append(j[1])

    # Neural Network Configuration
    step = 5
    clf = MLPClassifier(
        solver="lbfgs",
        alpha=1e-05,

        # Use Sigmoid activation function
        activation="logistic",

        learning_rate="constant",
        learning_rate_init=0.001,

        # Number of neurons per layer
        hidden_layer_sizes=(25, 25, 25, 25, 25), 

        # PRNG Seed
        random_state=1
    )

    # Train
    logging.info("Fitting MLP with {} features and {} samples".format(len(features), len(samples)))
    clf.fit(features, samples)

    # Test predictions
    # TODO

if __name__ == "__main__":
    main()
