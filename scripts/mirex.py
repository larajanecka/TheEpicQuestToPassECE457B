import wavParser as wav

# Retrieve all MIREX wav files from a directory
# Assume files are in the format train{index}.wav, train{index}.txt,
def get_mirex_wav_files(directory):
    files = []
    for i in xrange(1,4):

        # Extract beats from file. Use first beat interpretation as correct though
        # there are 10-11. TODO: Is there a better way?
        file_name = "{}/train{}.txt".format(directory, str(i))
        wav_name = "{}/train{}.wav".format(directory, str(i))

        beats = []
        with open(file_name, "r") as beats_file:
            beats = beats_file.readline().rstrip().split("\t") 

        waveform, samplingRate, bitsPerSample = wav.getRawWaveData(wav_name)
        files.append(WavFile(file_name, waveform, samplingRate, bitsPerSample, beats))

    return files

# A class representing all necessary information from a WavFile
class WavFile():
    def __init__(self, absoluteName, waveform, samplingRate, bitsPerSample, beats):
        self.absoluteName = absoluteName
        self.waveform = waveform
        self.samplingRate = samplingRate
        self.bitsPerSample = bitsPerSample
        self.beats = beats
