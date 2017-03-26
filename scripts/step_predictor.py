import random

# Predict when the next 
# period - the length of time for each array entry
# Example : beats = [0.4, 0.0, 0.1, 0.7], period = 0.5 (seconds) for a song of 2s
def predict_steps(beats, period):
    # Return the times when steps occur
    steps = []

    # If more than 1s has passed, it is a step
    # If less than 1s has passed, prob = diff_time^3
    def probability_of_step(last_step, beat_time):
        if diff > 1:
            return 1.0
        return (beat_time - last_step) ** 3

    # Calculate the probability a given beat is a step given the probability
    # the time is a beat and the time since the last step
    for b in beats:
        last_step_probability = probability_of_step(steps[-1] if len(steps) > 0 else 0, b)
        probability = b * last_step_probability
        if random.uniform(0.0, 1.0) <= probability:
            steps.append(b * period)

   return steps 
