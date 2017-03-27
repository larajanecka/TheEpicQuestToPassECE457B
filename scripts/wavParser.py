# Wav specs http://soundfile.sapp.org/doc/WaveFormat/

import threading
from Tkinter import *	# Simple GUI
import time

# Little Endian
def getIntFromBytes(bytes):
	total = 0
	for i in range(0, len(bytes)):
		total += ord(bytes[i]) << (i * 8)
	return total

# Waveform list elements corresponds to the different channels.
# Every amplitude value go from -2^(bitsPerSample-1) to 2 ^ bitsPerSample
def getRawWaveData(filename):
	data = []
	with open(filename, 'rb') as f:
		data = f.read(44)	# Wav file metadata length. Should remain this till the end of time.

	chunkSize = getIntFromBytes(data[4:8])	# We might not need this.
	audioFormat = getIntFromBytes(data[20:21])
	numChannels = getIntFromBytes(data[22:23])
	sampleRate = getIntFromBytes(data[24:28])
	byteRate = getIntFromBytes(data[28: 32])
	blockAlign = getIntFromBytes(data[32:34])	# We might not need this.
	bitsPerSample = getIntFromBytes(data[34:35])
	dataSize = getIntFromBytes(data[40:44])

	# print "chunkSize %s" % chunkSize
	# print "audioFormat %s" % audioFormat
	# print "numChannels %s" % numChannels
	# print "sampleRate %s" % sampleRate
	# print "byteRate %s" % byteRate
	# print "blockAlign %s" % blockAlign
	# print "bitsPerSample %s" % bitsPerSample
	# print "dataSize %s" % dataSize

	assert(audioFormat == 1)	# 1 for uncompressed
	assert(byteRate == sampleRate * numChannels * bitsPerSample / 8) # Assertion suggested by Wav specs
	waveform = []
	# 1 Waveform for each channel.
	for i in range(0, numChannels):
		waveform.append([])

	with open(filename, 'rb') as f:
		f.read(44)	# Skip meta data
		for i in range(0, (dataSize * 8 / bitsPerSample) / numChannels):
			for j in range(0, numChannels):
				waveHeight = getIntFromBytes(f.read(bitsPerSample/8))
				waveform[j].append(waveHeight)

	return waveform, sampleRate, bitsPerSample

def playWindowsFile(filename):
        import winsound	# Windows sound stuff. Since only for debugging we'll just use this.
	winsound.PlaySound(filename, winsound.SND_FILENAME)

# TODO: Lets consider making a killable thread to make debugging easier
def playFileAsync(filename):
	threading.Thread(target=playWindowsFile, args=(filename,)).start()
	return time.clock()

# Waveform passed to the GUI should be the preprocessed display height that we want per sample
def guiWave(waveform, sampleRate, bitsPerSample, songStart):
	frameRefresh = 0.01	# How much time for attempting frame refresh
	master = Tk()
	w = Canvas(master, width=len(waveform) * 100, height=200)	# width based on number of channels
	w.pack()

	totalTime = float(len(waveform[0])) / sampleRate
	i = 0
	while i <= int(totalTime * (1 / frameRefresh)):
		i += 1
		songElapsedTime = time.clock() - songStart
		guiTime = i * frameRefresh
		if songElapsedTime > guiTime + frameRefresh:
			i += int((songElapsedTime - guiTime) / frameRefresh)
		else:
			while songElapsedTime < guiTime:
				songElapsedTime = time.clock() - songStart
		#Draw
		for j in range(0, len(waveform)):
			height = waveform[j][i]
			guiHeight = float(height) / pow(2, bitsPerSample * 2) * 200

			w.create_rectangle(j * 100, 0, (j + 1) * 100, 200, fill="white")
			w.create_rectangle(j * 100, 0, (j + 1) * 100, guiHeight, fill="blue")
			master.update()
		#print guiTime

def getReducedWaveform(originalWaveform, sampleRate, bitsPerSample):
	secondDenomination = 0.01	# How much time for each frame
	frameLength = 2 # How many frame's worth of samples to average for each frame

	# Confusing variable names 
	samplesPerFrame = int(secondDenomination * sampleRate)
	resultingFrames = int(len(originalWaveform[0]) * secondDenomination)

	energy = []
	for w in originalWaveform:
		energy.append([pow(x - pow(2, bitsPerSample - 1), 2) for x in w])


	outputWaveform = []
	for e in energy:
		waveform = []
		for i in range(0, frameLength):	# First few frames need to be 0 for this algorithm.
			waveform.append(0)
		for i in range(frameLength, resultingFrames - frameLength):
			waveform.append(sum(e[samplesPerFrame * (i - frameLength): samplesPerFrame * (i + frameLength + 1)]) / ((1 + 2 * frameLength)* samplesPerFrame))
		outputWaveform.append(waveform)

	return outputWaveform, samplesPerFrame

# Reduce number of samples in the original waveform
def compressWaveForm(originalWaveform, sampleRate, bitsPerSample, newSampleRate):
	secondDenomination = 1.0/newSampleRate	# How much time for each frame

	# Confusing variable names 
	samplesPerFrame = int(secondDenomination * sampleRate)
	frameLength = 0 # How many frame's worth of samples to average for each frame
	resultingFrames = int(len(originalWaveform) * sampleRate / newSampleRate)

	waveform = []
	for i in range(0, frameLength + 1):	# First few frames need to be 0 for this algorithm.
		waveform.append(0)
	for i in range(frameLength, resultingFrames - frameLength):
		waveform.append(sum(originalWaveform[samplesPerFrame * (i - frameLength): samplesPerFrame * (i + frameLength + 1)]) / ((1 + 2 * frameLength)* samplesPerFrame))

	return waveform

def getAbsoluteAmplitude(originalWaveform, bitsPerSample):
	axis = pow(2, bitsPerSample - 1)
	newWaveForm = []
	for o in originalWaveform:
		newWaveForm.append(abs((o - axis)/ axis))
	return newWaveForm

def debug():
	filename = "Ltheme2.wav"
	waveform, sampleRate, bitsPerSample = getRawWaveData(filename)
	# This is arbirtrary code for better visualisation. The formula for energy should be waveHeight ^ 2.
	reducedWaveform, reducedSampleRate = getReducedWaveform(waveform, sampleRate, bitsPerSample)
	songStart = playFileAsync(filename)
	#songStart = time.clock()
	guiWave(reducedWaveform, reducedSampleRate, bitsPerSample, songStart)

#debug()
