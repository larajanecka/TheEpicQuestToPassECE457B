import glob
import matplotlib.pyplot as plt
import numpy as np
import threading
import wavParser as wav
import wave

# Extract beats from file. Use first beat interpretation as correct though
# there are 10-11. TODO: Is there a better way?
def get_wav_file(wav_file_name, beat_file_name):
    beats = []
    with open(beat_file_name, "r") as beat_file:
        beats = [ float(b) for b in beat_file.readline().rstrip().split(",") ] 

    waveform, samplingRate, bitsPerSample = wav.getRawWaveData(wav_file_name)
    song_name = wav_file_name[:len(wav_file_name) - 4].split('/')[-1]
    
    wfile = wave.open(wav_file_name, 'r')
    samplingRate = wfile.getframerate()
    frames = wfile.readframes(-1)
    print 'SIZE', len(frames)
    print 'FRAMES', np.fromstring(frames, 'Int16')
    plt.plot(np.fromstring(frames, 'Int16')[0:200000])
    plt.show()
    #bitsPerSample = 

    return WavFile(song_name, wav_file_name, waveform, samplingRate, bitsPerSample, beats) 

t,u,v =  wav.getRawWaveData('./POSSESSION.wav')
print len(t), len(t[0]) 

# A generator for retrieving files 
def get_wav_files(directory):
    files = []
    print directory
    for wav_file in glob.glob(directory + "*.wav"):
        beat_file = wav_file[:len(wav_file) - 4] + ".beats"
        wav_object = get_wav_file(wav_file, beat_file)
        yield wav_object



# A class representing all necessary information from a WavFile
BEAT_ERROR = 0.3
class WavFile():
    def __init__(self, songName, absoluteName, waveform, samplingRate, bitsPerSample, beats):
        self.songName = songName
        self.absoluteName = absoluteName
        self.waveform = waveform
        self.samplingRate = samplingRate
        self.bitsPerSample = bitsPerSample
        self.beats = beats

    # Determine if a given time is a beat
    # Use binary search to determine if time is within ERROR of an actual beat
    def isBeat(self, time):
        i = 0
        j = len(self.beats) - 1
        found = False

        while i <= j and not found:
            mid = (i + j) // 2
            beat_time = self.beats[mid]

            if abs(time - beat_time) <= 0.005:
                return True
            else:
                if time < self.beats[j]:
                    j = mid - 1 
                else:
                    i = mid + 1

        return False
                


