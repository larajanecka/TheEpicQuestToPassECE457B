# Beat Detection from audio files to generate Stepmania Dance Files using Neural Networks

Our goal is to provide the times of beats in a given song to generate Stepmania/DDR step files.

## Setup Process

### Retrieve datasets

In order to train the neural network, we need a dataset of audio files with beat annotations.
We use the MillionSongSubset collection

To retrieve this dataset execute:
`./datasets/get.sh`

Next, you must parse the dataset and download the media files for each song. Note, you need a GooglePlayMusic account to do this. The data should be committed or archived in some directory.
```
export EMAIL=<google_play_music_email>
export PASSWORD=<google_account_pw>
python generate_dataset.py datasets/MillionSongSubset/data/<any_subdir> out/ <num_of_songs
```

Now, for each song you will have an `.mp3, .wav, .beats` file in out.

### Generate datasets and Train Neural Network

TODO: `mlp_bg.py` currently uses the mirex dataset but it should use the MillionSongSubset

### Output StepMania files

