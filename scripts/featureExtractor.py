import wavParser
from math import floor
from scipy.fftpack import fft, fftfreq
from numpy import sqrt, arctan, pi
import matplotlib.pyplot as plt
# add calculation to get peak frequency
# calculate change in peak frequency with next value
# change aggregation functions to have overlap

# Size of the chunk to aggregate
chunkSize = 441
# Frequency bands
breakFrequencies = [200,400,800,1600,3200]


# sum channels
def sumChannels(waveform):
	summed = []
	for i in range(0, len(waveform[0])):
		total = 0
		for k in range(0, len(waveform)):
			total += waveform[k][i]**2
		summed.append(total)
	return summed

# iterate over total waveform and average chunks
def chunkDataAverage(waveform):
	numSamples = len(waveform)
	averagedAmplitudes = []
	for i in range(0, int(floor(numSamples / chunkSize)) - 1):
		# sum energy level over chunk
		total = 0
		for j in range(i, i+chunkSize):
			total += waveform[j]
		averagedAmplitudes.append(total / chunkSize)
	return averagedAmplitudes

def getVariances(waveform, sampleRate):
	numSamples = len(waveform)
	chunksPerSecond = int(floor(sampleRate/chunkSize))

	halfWindowSize =  int(floor(chunksPerSecond/2))

	# building first half window
	secondWindowSum = 0
	for i in range(0, chunksPerSecond):
		secondWindowSum += waveform[i]

	variances = []
	for i in range(0, numSamples):
		windowSize = chunksPerSecond
		if i >= halfWindowSize:
			windowSize += i

		if i < numSamples - halfWindowSize:
			windowSize -= (numSamples - i + 1)

		variances.append(waveform[i] - (secondWindowSum / windowSize))

		if i >= halfWindowSize:
			secondWindowSum -= waveform[i - halfWindowSize]

		if i < numSamples - halfWindowSize:
			secondWindowSum += waveform[i + halfWindowSize]

	return variances

def testVarience():
	filename = "Ltheme2.wav"
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)

	averagedWaveform = chunkDataAverage(waveform)
	variances = getVariances(averagedWaveform, sampleRate)
	return variences


def chunkBandwidthEnergies(waveform, sampleRate):
	bandwidthEnergies = []

	freqs = fftfreq(chunkSize, 0.000022676)
	for i in range(0, len(waveform), chunkSize):
		chunkEnergies = []
		fourier = fft(waveform[i:i+chunkSize])
		binNumber = 0
		binTotal = 0
		maxFreq = 0
		maxAmp = 0
		# data is symmetrical, ignore last half
		for j in range(1, int(len(fourier)/2 + 1)):
			# ignore frequencies above 3200
			if freqs[j] > breakFrequencies[-1]:
				break
			value = fourier[j]
			# sum energy in band width
			if binNumber < len(breakFrequencies) and freqs[j] > breakFrequencies[binNumber] :
				chunkEnergies.append(binTotal)
				binNumber += 1
				binTotal = 0
			amp = value.real**2 + value.imag**2
			binTotal += amp

			# keep track of frequency with max amplitude
			maxAmp = max(maxAmp, amp)
			if maxAmp == amp:
				maxFreq = freqs[j]
		bandwidthEnergies.append(chunkEnergies)
		bandwidthEnergies.append(maxFreq)
	return bandwidthEnergies

# pass in a second's worth of data
def getBandwidthVariance(dataSet, sampleRate):
	numSamples = len(dataSet)
	bands = len(breakFrequencies)
	chunksPerSecond = int(floor(sampleRate/chunkSize))

	halfWindowSize =  int(floor(chunksPerSecond/2))

	# building first half window
	secondWindowSum = [0] * bands
	for i in range(0, chunksPerSecond):
		for j in range(0, bands):
			secondWindowSum[j] += dataSet[i][j]

	variances = []
	for i in range(0, numSamples):
		windowSize = chunksPerSecond

		if i >= halfWindowSize:
			windowSize += i

		if i < numSamples - halfWindowSize:
			windowSize -= (numSamples - i + 1)

		bandVariance = []
		for j in range(0, bands):
			bandVariance.append(dataSet[i][j] - (secondWindowSum[j] / windowSize))

			if i >= halfWindowSize:
				secondWindowSum[j] -= dataSet[i - halfWindowSize][j]

			if i < numSamples - halfWindowSize:
				secondWindowSum[j] += dataSet[i + halfWindowSize][j]
		variances.append(bandVariance)
	return variances

def testBandWidthVariences(waveform):
	filename = "Ltheme2.wav"
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)
	averages = chunkBandwidthEnergies(waveform, sampleRate)
	variances = getBandwidthVariance(averages)


def getFeatures(filename):
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)
	summedWaveform = sumChannels(waveform)
	# averagedWaveform = chunkDataAverage(summedWaveform)
	# variances = getVariances(averagedWaveform, sampleRate)
	bandwidthAverages = chunkBandwidthEnergies(summedWaveform, sampleRate)
	print bandwidthAverages[0]
	print summedWaveform[0]
	# bandwidthAverages = getBandwidthVariance(bandwidthAverages, sampleRate)


getFeatures("Ltheme2.wav")
