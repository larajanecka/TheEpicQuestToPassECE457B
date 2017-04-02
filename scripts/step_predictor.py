import random

# Predict when the next step will occur, given the probability a time_frame represents a beat
# period - the length of time (s) for each timeframe
# Args
#  - beats = [0.4, 0.0, 0.1, 0.7] (probability of a beat per timeframe)
#  - period = 0.5 (time in seconds per beat)
def predict_steps(beats, period):
    # Return the times when steps occur
    steps = []

    # If more than 1s has passed, it is a step
    # If less than 1s has passed, prob = diff_time^3
    def probability_of_step(last_step):
        last_step = 1 if last_step > 1 else last_step
        return last_step ** 2

    # Calculate the probability a given beat is a step given the probability
    # the time is a beat and the time since the last step
    lastStepIndex = 0
    i = 0
    for b in beats:
        last_step_time = (len(steps) - lastStepIndex)*period if len(steps) > 0 else 0 
        last_step_probability = probability_of_step(last_step_time)
        probability = b * last_step_probability
        #print "%s %s " %(last_step_time, last_step_probability)
        if random.uniform(0.0, 1.0) <= probability:
            steps.append(1.0)
            lastStepIndex = i
        else:
            steps.append(0.0)
        i += 1

    return steps 
