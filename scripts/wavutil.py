import glob
import threading
import wavParser as wav


# Extract beats from file. Use first beat interpretation as correct though
# there are 10-11. TODO: Is there a better way?
def get_wav_file(wav_file_name, beat_file_name):
    beats = []
    with open(beat_file_name, "r") as beat_file:
        beats = beat_file.readline().rstrip().split(",") 

    waveform, samplingRate, bitsPerSample = wav.getRawWaveData(wav_file_name)
    return WavFile(wav_file_name, waveform, samplingRate, bitsPerSample, beats) 

# A generator for retrieving files 
def get_wav_files(directory):
    files = []
    for wav_file in glob.glob(directory + "*.wav"):
        print "Getting file", wav_file
        beat_file = wav_file[:len(wav_file) - 4] + ".beats"
        wav_object = get_wav_file(wav_file, beat_file)
        yield wav_object

# A class representing all necessary information from a WavFile
class WavFile():
    def __init__(self, absoluteName, waveform, samplingRate, bitsPerSample, beats):
        self.absoluteName = absoluteName
        self.waveform = waveform
        self.samplingRate = samplingRate
        self.bitsPerSample = bitsPerSample
        self.beats = beats
