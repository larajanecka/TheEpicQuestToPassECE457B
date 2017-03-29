# We will use width to refer to |neurons| per layer
#			height to refer to |layer|
from random import *
import math
class ActivationFunction(object):
	def __init__(self):
		pass

	@classmethod
	def getSigmoid(self, value):
                print value
		return 1 / (1 + math.exp(-1 * value))
		# if value > 0:
		# 	return 1
		# else:
		# 	return 0

	@classmethod
	def getDerivativeSigmoid(self, value):
		return value

class Neuron(object):
	def __init__(self, width, index, learningRate):
		self.width = width
		maxWeight = 2.0 / width
		self.weights = [(random() * maxWeight - maxWeight / 2) for i in range(width)]
		self.currentInputBuffer = [0 for i in range(width)]
		self.error = 0
		self.value = 0
		self.index = index
		self.learningRate = learningRate

	def setChildrenAndParent(self, childNeurons, parentNeurons):
		self.childNeurons = childNeurons
		self.parentNeurons = parentNeurons

	def propagateData(self):
		self.value = 0
		for i in range(self.width):
			self.value += self.weights[i] * self.currentInputBuffer[i]
			#print "%s %s" % (self.weights[i] * self.currentInputBuffer[i], self.value)
		self.value = ActivationFunction.getSigmoid(self.value)
		for child in self.childNeurons:
			child.currentInputBuffer[self.index] = self.value

	def calculateError(self):
		summation = 0
		for child in self.childNeurons:
			summation += child.error * child.weights[self.index]
		self.error = self.value * (1 - self.value) * summation
		self.updateWeight()

	def updateWeight(self):
		for i in range(self.width):
			self.weights[i] += self.currentInputBuffer[i] * self.error * self.learningRate


class OutputNode(Neuron):
	def __init__(self, width, index, learningRate):
		super(OutputNode, self).__init__(width, index, learningRate)

	def setExpectedOutput(self, expectedOutput):
		self.expectedOutput = expectedOutput

	def calculateError(self):
		self.error = (self.expectedOutput - self.value) * self.value * (1 - self.value)
		self.updateWeight()


# Minimal 3 layers
class BPM(object):
	def __init__(self, width=None, height=None, learningRate=None, dataSize=None, filename=None):
		if filename:
			self.data = None
			with open(filename, 'r') as f:
				self.data = f.readlines()
			header = self.data[0].split(' ')
			self.width = int(header[0])
			self.height = int(header[1])
			self.learningRate = float(header[2])
			self.dataSize = int(header[3])
		else:
			self.width = width
			self.height = height
			self.dataSize = dataSize
			self.learningRate = learningRate
		self.outputNodes = [OutputNode(self.width, i, self.learningRate) for i in range(self.dataSize)]
		self.neurons = [[] for i in range(self.height)]
		self.neurons[0] = [Neuron(self.dataSize, i, self.learningRate) for i in range(self.width)]
		for j in range(1, self.height):
			self.neurons[j] = [Neuron(self.width, i, self.learningRate) for i in range(self.width)]
		for i in range(self.width):
			self.neurons[0][i].setChildrenAndParent(self.neurons[1], [])
		for i in range(self.dataSize):
			self.outputNodes[i].setChildrenAndParent([], self.neurons[self.height - 1])
		for j in range(1, self.height - 1):
			for i in range(self.width):
				self.neurons[j][i].setChildrenAndParent(self.neurons[j + 1], self.neurons[j - 1])
		for i in range(self.width):
			self.neurons[self.height - 1][i].setChildrenAndParent(self.outputNodes, self.neurons[self.height - 2])

		# Populate weights
		if filename:
			currentIndex = 1
			for i in range(self.width):
				weights = [float(w) for w in self.data[currentIndex].split(' ')]
				currentIndex += 1
				self.neurons[0][i].weights = weights
			for j in range(1, self.height):
				for i in range(self.width):
					weights = [float(w) for w in self.data[currentIndex].split(' ')]
					currentIndex += 1
					self.neurons[j][i].weights = weights
			for i in range(self.dataSize):
				weights = [float(w) for w in self.data[currentIndex].split(' ')]
				currentIndex += 1
				self.outputNodes[i].weights = weights

	# Header line
	# |width| lines of input node weights. line contains |dataSize| elements
	# |width * (height - 1)| lines of node weights. line contains |width| elements
	# |dataSize| lines of output node weights. line contains |width| elements
	def exportToFile(self, filename):
		f = open(filename, 'w')
		f.write("%s %s %s %s\n" % (self.width, self.height, self.learningRate, self.dataSize))
		inLine = "%s"
		regularLine = "%s"
		for i in range(self.dataSize - 1):
			inLine += " %s"
		for i in range(self.width - 1):
			regularLine += " %s"
		inLine += "\n"
		regularLine += "\n"
		for i in range(self.width):
			f.write(inLine % tuple(self.neurons[0][i].weights))
		for j in range(1, self.height):
			for i in range(self.width):
				f.write(regularLine % tuple(self.neurons[j][i].weights))
		for i in range(self.dataSize):
			f.write(regularLine % tuple(self.outputNodes[i].weights))
		f.close()

	def iterate(self, inputData, outputData=None, modify=True):
		#import pdb;pdb.set_trace()
		error = 0
		for i in range(self.width):
			for j in range(self.dataSize):
				self.neurons[0][i].currentInputBuffer[j] = inputData[j]
		for j in range(self.height):
			for i in range(self.width):
				self.neurons[j][i].propagateData()

		for i in range(self.dataSize):
			self.outputNodes[i].propagateData()

		# Back propagate
		if modify:
			for i in range(self.dataSize):
				#print inputData[i]
				self.outputNodes[i].setExpectedOutput(outputData[i])
			for i in range(self.dataSize):
				self.outputNodes[i].calculateError()
				error += abs(self.outputNodes[i].error)
			j = self.height
			while(j > 0):
				j -= 1
				for i in range(self.width):
					self.neurons[j][i].calculateError()

		return error

	def getMembershipFromSong(self, waveform):
		outputWaveform = []
		for i in range(len(waveform) / self.dataSize):
			self.iterate(inputData=waveform[i*self.dataSize : (i+1) * self.dataSize], modify=False)
			for o in self.outputNodes:
				outputWaveform.append(o.value)
		return outputWaveform


# Refactor and rename. doing more than just debug
def debug():
	from wavParser import getRawWaveData, compressWaveForm, getAbsoluteAmplitude
	from stepsParser import getBeatSamples
	songFile = "POSSESSION.wav"
	stepsFile = "POSSESSION.sm"
	networkSampleRate = 4410 # Sample rate to be used by the network
	print "reading waveform..."
	waveform, sampleRate, bitsPerSample = getRawWaveData(songFile)
	singleChannel =  compressWaveForm(waveform[0], sampleRate, bitsPerSample, networkSampleRate)
	singleChannel = getAbsoluteAmplitude(singleChannel, bitsPerSample)

	print "reading steps file..."
	beatSamples = getBeatSamples(stepsFile, networkSampleRate)
	mostDenseSample = beatSamples[len(beatSamples) - 1]

	print "start"
	width = 10
	dataSize = 100
	network = BPM(width, 5, 0.1, dataSize)
	#network = BPM(filename="networks/32.net")
	epoch = 0
	temp = 0
	cumulativeError = 1
	while abs(cumulativeError) >= 0.00001:
		cumulativeError = 0
		for i in range(len(mostDenseSample) / dataSize):
			cumulativeError += network.iterate(singleChannel[i*dataSize : (i+1) * dataSize], mostDenseSample[i*dataSize : (i+1) * dataSize])
			#print "%s error: %s" % (i, cumulativeError)
		epoch += 1
		network.exportToFile("networks/%d.net" % epoch)
		print "epoch %d, \t cumulativeError %s" % (epoch, cumulativeError)

def debugDaniel():
	from wavParser import getRawWaveData, compressWaveForm, getAbsoluteAmplitude
	songFile = "POSSESSION.wav"
	networkSampleRate = 4410 # Sample rate to be used by the network
	print "reading waveform..."
	waveform, sampleRate, bitsPerSample = getRawWaveData(songFile)
	singleChannel =  compressWaveForm(waveform[0], sampleRate, bitsPerSample, networkSampleRate)
	singleChannel = getAbsoluteAmplitude(singleChannel, bitsPerSample)

	print "Neural net..."
	network = BPM(filename="networks/250.net")
	outputMemberShip = network.getMembershipFromSong(singleChannel)

	# btw this is a very bad outputmembership function, but lets work with this first.
	import pdb;pdb.set_trace()

#debugDaniel()
