# Steps sepcs http://ec2.stepmania.com/wiki/The_.SM_file_format
from operator import itemgetter

stepTypes = ["0", "1", "2", "3", "4", "M", "L", "F", "S"]
# Change this to enum if we actually end up using this
# 0 = no note here
# 1 = a regular "tap note"
# 2 = beginning of a "Frezze Arrow" (hold note)
# 3 = end of a "Frezze Arrow"
# 4 = beginning of a roll (3.9+, 3.95+, 4.0)
# M = Mine or shock arrow
# L = Lift (3.9+ and 4.0)
# F = Fake (5.0)
# S = Shock Arrow (3.9 AMX only)

def isDigit(char):
	return char in "1234567890."

def parseIntFloatPairString(pString):
	data = []
	for i in range(0, len(pString)):
		if pString[i] == "=":
			j = i - 1	# j will be the start index of the number before "="
			while isDigit(pString[j]):
				j -= 1
			k = i + 1	# k will be the end index of the number before "="
			while isDigit(pString[k]):
				k += 1
			data.append([int(float(pString[j + 1: i])), float(pString[i + 1: k])])
	return data

# Assume data is split by "#"
def getRawStepData(filename):
	data = None
	with open(filename, 'r') as f:
		data = f.readlines()

	# We define metadata for this kind of file as everything before "#NOTES"
	# Parse metadata
	offset = None
	bpmString = ''
	stopString = ''
	startBpmString = False
	startStopString = False
	notesIndexList = []
	i = 0
	for datum in data:
		if datum[0:6] != "#NOTES":
			if datum[0:7] == "#OFFSET":
				offset = float(datum[8: datum.index(";")])
			if datum[0] == "#":	# Used for multi line attributes
				startBpmString = False
				startStopString = False
			if startBpmString:
				bpmString += datum
			if startStopString:
				stopString += datum
			if datum[0:5] == "#BPMS":
				startBpmString == True
				bpmString = (datum + ' ')[5: -1]
			if datum[0:6] == "#STOPS":
				startStopString = True
				stopString = (datum + ' ')[6: -1]
		else:
			notesIndexList.append(i)
		i += 1
	notesIndexList.append(i)

	stops = parseIntFloatPairString(stopString)	# This is a list of (measure#, stopDuration)
	bpms = parseIntFloatPairString(bpmString)	# This is a list of (measure#, bpm)
	stops = sorted(stops, key=itemgetter(0))
	bpms = sorted(bpms, key=itemgetter(0))

	stepLists = []
	for i in range(0, len(notesIndexList) - 1):
		isDanceSingle = False
		j = notesIndexList[i]
		steps = []
		metaCount = 0
		while metaCount <= 5:
			if ":" in data[j]:
				metaCount += 1
				if "dance-single" in data[j]:
					isDanceSingle = True
			j += 1
		if not isDanceSingle:	# Only care about this kind of steps for now.
			continue
		measure = []
		while j != notesIndexList[i + 1]:
			if data[j][0] == ",":
				steps.append(measure)
				measure = []
			elif data[j][0] in stepTypes:
				measure.append(data[j])
			j += 1
		stepLists.append(steps)

	# for steps in stepLists:
	# 	print "---------------------------------------------"
	# 	for measure in steps:
	# 		for note in measure:
	# 			print note
	# 		print ","
	return stepLists, bpms, stops, offset

# bpms, offset, and stops are properties of the stepList. SampleRate is the property of the output you want.
# return list of samples with rate SampleRate. zero for no steps, non-zero for steps.
def getBeatSamplesFromStepList(stepList, bpms, stops, offset, sampleRate):
	elapsedTime = 0.0	# Time of output sampleList
	gameTime = -offset	# Time of steplist
	stepListIndex = 0
	sampleListIndex = 0
	sampleList = [0]
	currentBpmIndex = 0
	currentBpm = None
	currentStopIndex = 0
	while stepListIndex < len(stepList):
		measure = stepList[stepListIndex]
		lineFraction = (4 + 0.0001) / float(len(measure)) # Each measure has 4 wholes
		totalFraction = 0.0
		for line in measure:
			if currentBpmIndex < len(bpms) and bpms[currentBpmIndex][0] == stepListIndex * 4 + int(totalFraction):
				currentBpm = bpms[currentBpmIndex]
				currentBpmIndex += 1
			if currentStopIndex < len(stops) and stops[currentStopIndex][0] == stepListIndex * 4 + int(totalFraction):
				gameTime += stops[currentStopIndex][1]
				currentStopIndex += 1
			while elapsedTime <= gameTime:
				elapsedTime += 1.0 / sampleRate
				sampleListIndex += 1
				sampleList.append(0)
			# We would need to change the complexity of this parsing once we can accomodate other step types.
			if "1" in line or "2" in line:
				sampleList[sampleListIndex] = 1

			totalFraction += lineFraction
			gameTime += 1.0 / (currentBpm[1] / 240 * len(measure))

		stepListIndex += 1
	return sampleList

# This function currently only works for 44100 sample rate and a few other constants.
def replicateWavFile(filename, beatSamples):
	from wavParser import getRawWaveData
	header = None
	with open(filename, 'rb') as f:
		header = f.read(44)	# Wav file metadata length. Should remain this till the end of time.
	targetFile = open("step%s" % filename, 'w')
	targetFile.write(header)
	i = 0
	sampleCount = len(beatSamples)
	while i < sampleCount:
		if beatSamples[i]:
			targetFile.write('ffff')
		else:
			targetFile.write('0000')
		i += 1
	targetFile.close()

def debug():
	# Raw data by meassures
	songFile = "POSSESSION.wav"
	fileName = 'POSSESSION.sm'
	stepLists, bpms, stops, offset = getRawStepData(fileName)

	# Consider also parsing a difficulty and including it in this data
	beatSamples = []
	for stepList in stepLists:
		beatSample = getBeatSamplesFromStepList(stepList, bpms, stops, offset, 44100)
		beatSamples.append(beatSample)

	replicateWavFile(songFile, beatSamples[0])

# debug()

