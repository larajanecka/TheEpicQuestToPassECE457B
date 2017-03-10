import wavParser as wav
from sklearn.neural_network import MLPClassifier

# This program uses a multilayer perceptron in an attempt to identify beats in songs
# The feature used from audio files are the aggregate of the amplitudes of multiple
# channels per unit time

def main():
    waveform, sampleRate, bitsPerSample = wav.getRawWaveData("Ltheme2.wav")
    print "There are", len(waveform), "channels"
    print "Sample rate is", sampleRate
    print "BitsPerSample is", bitsPerSample
    r = summationSquared(waveform)
    print len(waveform[0])
    print len(r)

    # Neural Network Configuration
    step = 5
    length = len(r)
    clf = MLPClassifier(
        solver="lbfgs",
        alpha=1e-05,
        hidden_layer_sizes=(5,2),
        random_state=1
    )

    # Train

    #Fit
    for frame in xrange(0, length, step):
        pass

# Functions used to aggregate channels

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
