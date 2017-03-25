import wavParser
from math import floor
from scipy.fftpack import fft
from numpy import sqrt, arctan, pi
import matplotlib.pyplot as plt

# Size of the chunk to aggregate
chunkSize = 441
# Frequency bands
breakFrequencies = [2000,4000,8000,16000,32000]

# iterate over total waveform and average chunks
def chunkDataAverage(waveform):
	numSamples = len(waveform)
	averagedAmplitudes = []
	for i in range(0, int(floor(numSamples / chunkSize)) - 1):
		# sum energy level over chunk
		total = 0
		for j in range(i, i+chunkSize):
			# calculate energy level, summed square over all channels
			for k in range(0, len(waveform))
				total += waveform[k][j]**2
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
			windowSize -= (numSamples - i)


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

# pass in a chunk's worth of data
def chunkBandwidthAverage(waveform, sampleRate):
	bandWidthAverages = []
	# TODO: check this
	hertzPerBin = sampleRate / chunkSize

	for i in range(0, len(waveform), chunk):
		chunkAverages = []
		fourier = fft(waveform[i:i+chunk])
		binNumber = 0
		binCount = 0
		binTotal = 0
		for j in fourier:
			if j*hertzPerBin > breakFrequencies[binNumber] :
				chunkAverages.append(binTotal/binCount)
				binNumber += 1
				binTotal = 0
				binCount = 0
			amp = sqrt(i.real**2 + i.imag**2)
			binTotal += amp
			binCount ++
		bandwidthAverages.append(chunkAverages)
	return bandwidthAverages

# pass in a second's worth of data
def getBandwidthVariance(dataSet):
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
			windowSize -= (numSamples - i)

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
	averages = chunkBandwidthAverage(waveform, sampleRate)
	variances = getBandwidthVariance(averages)


