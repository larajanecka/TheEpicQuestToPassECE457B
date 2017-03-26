# We will use width to refer to |neurons| per layer
#			height to refer to |layer|
class ActivationFunction(object):
	def __init__(self):
		pass

	@classmethod
	def getSigmoid(self, value):
		return value

	@classmethod
	def getDerivativeSigmoid(self, value):
		return value

class Neuron(object):
	def __init__(self, width, index, learningRate):
		self.width = width
		self.weights = [0 for i in range(width)]
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
		self.propagateData()
		self.error = (self.expectedOutput - self.value) * self.value * (1 - self.value)
		self.updateWeight()

# Minimal 3 layers
class BPM(object):
	def __init__(self, width, height, learningRate, dataSize):
		self.width = width
		self.height = height
		self.dataSize = dataSize
		self.outputNodes = [OutputNode(dataSize, i, learningRate) for i in range(dataSize)]
		self.neurons = [[] for i in range(height)]
		self.neurons[0] = [Neuron(dataSize, i, learningRate) for i in range(dataSize)]
		for j in range(1, height):
			self.neurons[j] = [Neuron(width, i, learningRate) for i in range(width)]
		for i in range(dataSize):
			self.neurons[0][i].setChildrenAndParent(self.neurons[1], [])
			self.outputNodes[i].setChildrenAndParent([], self.neurons[height - 1])
		for j in range(1, height - 1):
			for i in range(width):
				self.neurons[j][i].setChildrenAndParent(self.neurons[j + 1], self.neurons[j - 1])
		for i in range(width):
			self.neurons[height - 1][i].setChildrenAndParent(self.outputNodes, self.neurons[height - 2])

	def iterate(self, inputData, outputData):
		error = 0
		for i in range(self.dataSize):
			self.outputNodes[i].setExpectedOutput(outputData[i])
		for i in range(self.dataSize):
			self.neurons[0][i].currentInputBuffer[i] = inputData[i]
		for j in range(self.height):
			for i in range(self.width):
				self.neurons[j][i].propagateData()

		for i in range(self.dataSize):
			self.outputNodes[i].calculateError()
			error += self.outputNodes[i].error
		j = self.height
		while(j > 0):
			j -= 1
			for i in range(self.width):
				self.neurons[j][i].calculateError()

		return error

def debug():
	from wavParser import getRawWaveData, compressWaveForm
	from stepsParser import getBeatSamples
	songFile = "Ltheme2.wav"
	stepsFile = "POSSESSION.sm"
	networkSampleRate = 4410 # Sample rate to be used by the network
	print "reading waveform..."
	waveform, sampleRate, bitsPerSample = getRawWaveData(songFile)
	singleChannel =  compressWaveForm(waveform[0], sampleRate, bitsPerSample, networkSampleRate)

	print "reading steps file..."
	beatSamples = getBeatSamples(stepsFile, networkSampleRate)
	mostDenseSample = beatSamples[len(beatSamples) - 1]

	print "start"
	width = 20
	dataSize = 100
	network = BPM(width, 5, 0.1, dataSize)
	epoch = 0
	temp = 0
	cumulativeError = 1

	while cumulativeError >= 0.1:
		cumulativeError = 0
		for i in range(len(mostDenseSample) / dataSize):
			cumulativeError += network.iterate(singleChannel[i*dataSize : (i+1) * dataSize], mostDenseSample[i*dataSize : (i+1) * dataSize])
			print "%s error: %s" % (temp, cumulativeError)
			temp += 1
		epoch += 1
		temp = 0
		print "epoch %d" % epoch

debug()