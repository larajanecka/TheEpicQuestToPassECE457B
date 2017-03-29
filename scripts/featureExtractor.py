import wavParser
from math import floor, ceil
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
	for i in range(0, len(waveform), chunkSize):
		averagedAmplitudes.append(sum(waveform[i:i+chunkSize]))
	return averagedAmplitudes

def getVariances(waveform, sampleRate):
	numSamples = len(waveform)
	chunksPerSecond = int(floor(sampleRate/chunkSize))

	halfWindowSize =  int(floor(chunksPerSecond/2))

	# building first half window
	windowSum = 0
	for i in range(0, halfWindowSize):
		windowSum += waveform[i]

	variances = []
	windowSize = halfWindowSize
	for i in range(0, numSamples):
		if i < halfWindowSize:
			windowSum += waveform[i + halfWindowSize]
			windowSize += 1
		elif numSamples - i <= halfWindowSize:
			windowSum -= waveform[i - halfWindowSize]
			windowSize -= 1
		else:
			windowSum += waveform[i + halfWindowSize]
			windowSum -= waveform[i - halfWindowSize]

		variances.append(abs(waveform[i] - (windowSum / windowSize)))

	return variances

def testVarience():
	filename = "Ltheme2.wav"
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)

	averagedWaveform = chunkDataAverage(waveform)
	variances = getVariances(averagedWaveform, sampleRate)
	return variences

# output is total energy for each bandwidth and frequency with max energy
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

		chunkEnergies.append(binTotal)

		chunkEnergies.append(ceil(maxFreq))
		bandwidthEnergies.append(chunkEnergies)
	return bandwidthEnergies

# pass in a second's worth of data
# ouput is array for variance of each of the bands and the difference in peak frequency
def getBandwidthVariance(dataSet, sampleRate):
	numSamples = len(dataSet)
	bands = len(breakFrequencies)
	chunksPerSecond = int(floor(sampleRate/chunkSize))

	halfWindowSize =  int(ceil(chunksPerSecond/2))

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
		peakFrequencyDiff = abs(dataSet[i][-1] - dataSet[i+1][-1]) if i != numSamples - 1 else abs(dataSet[i-1][-1] - dataSet[i][-1])
		bandVariance.append(peakFrequencyDiff)
		variances.append(bandVariance)
	return variances

def testBandWidthVariences(waveform):
	filename = "Ltheme2.wav"
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)
	averages = chunkBandwidthEnergies(waveform, sampleRate)
	variances = getBandwidthVariance(averages)

def getFeatures(filename):
	waveform, sampleRate, bitsPerSample = wavParser.getRawWaveData(filename)
        chunk_size = sampleRate / 300
	summedWaveform = sumChannels(waveform)
	print len(summedWaveform)
	averagedWaveform = chunkDataAverage(summedWaveform)
	print len(averagedWaveform)
	variances = getVariances(averagedWaveform, sampleRate)
	print len(variances)
	bandwidthEnergies = chunkBandwidthEnergies(summedWaveform, sampleRate)
	print len(bandwidthEnergies)
	bandwidthVariance = getBandwidthVariance(bandwidthEnergies, sampleRate)
	print len(bandwidthVariance)

	if len(variances) != len(bandwidthVariance):
		sys.exit("Something has gone horribly wrong")

	vals = []
	for i in range(0, len(variances)):
		vals.append([variances[i]] + bandwidthVariance[i])

        return vals, chunk_size

	print vals[1]


getFeatures("Ltheme2.wav")
