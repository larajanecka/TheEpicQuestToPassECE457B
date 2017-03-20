import subprocess

# Requires ffmpeg to be in your $PATH environment variable

def convert_audio_file(input_file, output_file):
    return subprocess.call('ffmpeg -i {} {}'.format(input_file, output_file))
