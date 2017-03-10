import wavParser as wav
from sklearn.neural_network import MLPClassifier

# This program uses a multilayer perceptron in an attempt to identify beats in songs
# The feature used from audio files are the aggregate of the amplitudes of multiple
# channels per unit time

def main():
    waveform, sampleRate, bitsPerSample = wav.getRawWaveData("Ltheme2.wav")
    s2 = summationSquared(waveform)
    s = summation(waveform)

    # Neural Network Configuration
    step = 5
    length = len(s2)
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

    #Fit
    for frame in xrange(0, length, step):
        pass

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

if __name__ == "__main__":
    main()
