import os
import subprocess

# Converts between two audio file formats derived from the file extensions
# Only tested from .mp3 -> .wav
def convert_audio_file(input_file, output_file):
    converters = [
        ['ffmpeg', '-i', input_file, output_file],
        ['avconv', '-i', input_file, output_file],
    ]
    with open(os.devnull, 'w')  as FNULL:
        for c in converters:
            try:
                ret = subprocess.call(c, stdout=FNULL, stderr=FNULL)
                return
            except OSError as e:
                continue
        raise ConversionFailedException()

class ConversionFailedException(Exception):
    pass
