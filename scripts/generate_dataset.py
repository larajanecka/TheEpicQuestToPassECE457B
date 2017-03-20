from gmusicapi import Mobileclient
from gmusicapi import Webclient
from hdf5 import hdf5_getters
import json
import os
import sys
import urllib2
import audio_converter

# This program transforms HDF5 files into .mp3, .beat files per song
# Steps performed:
#  - Extract song metadata from a song in the MillionSongSubset
#  - Download song from GooglePlayMusic in mp3 form
#  - Convert mp3 song to wav
#  - Write beats file for song

def usage():
    print "usage: python generate_dataset.py <root_dir_of_hdf5_files> <output_directory> <#_of_songs_to_extract>"

# A wrapper class allowing you to download songs from GooglePlayMusic
class GMSongClient():

    # Extract Google Auth credentials from the environment
    def __init__(self):
        email = os.environ['EMAIL']
        pw = os.environ['PASSWORD']
        self.api = Mobileclient(debug_logging=False)
        self.api.login(email, pw, Mobileclient.FROM_MAC_ADDRESS, 'en_us')

    # Download a given song to a specified directory
    def download_song(self, artist, title, output_dir):
        query = '{} - {}'.format(artist, title)
        print 'Looking for', query

        # Search
        results = self.api.search(query, 100)['song_hits']
        print 'found', len(results), 'results'

        # Check for song
        song = ''
        for i in results:
            try:
                name = '{} - {}'.format(i['track']['artist'], i['track']['title'])
                if name.lower() == query.lower():
                    song = i
                    break
            except:
                pass
        if song == '':
            raise SongNotFoundException

        # Extract mp3 url
        store_id = song['track']['storeId']
        song_id = self.api.add_store_track(store_id)
        url = self.api.get_stream_url(song_id)

        # Download mp3 file
        mp3file = urllib2.urlopen(url)
        file_name = '{}{}.mp3'.format(output_dir, query)
        with open(file_name, 'wb') as output:
            output.write(mp3file.read())

class SongNotFoundException(Exception):
        pass

def write_beats_file(file_name, beats):
    text = ",".join(beats)
    with open(file_name, "w") as f:
        f.write(text)

def main():
    count = 0
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)

    data_dir = sys.argv[1]
    output_dir = sys.argv[2]
    num_songs = int(sys.argv[3])
    c = GMSongClient()

    # Walk the dataset tree
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            file_name = "/".join([root,f])
            print "Parsing file {}".format(file_name)
            
            # Retrieve HDF5 metadata
            h5 = hdf5_getters.open_h5_file_read(file_name)
            artist = hdf5_getters.get_artist_name(h5)
            song_title = hdf5_getters.get_title(h5)
            beats = ["%.4f" % beat for beat in hdf5_getters.get_beats_start(h5) ]
            song_name = "{} - {}".format(artist, song_title)
            print "Attempting to download song {}".format(song_name)

            # Download song
            try:
                c.download_song(artist, song_title, output_dir)
            except SongNotFoundException as e:
                print "Unable to download {}".format(song_name)
                continue

            # Convert song from mp3 to .wav
            base_filename = output_dir + song_name
            audio_converter.convert_audio_file(base_filename + ".mp3", base_filename + ".wav")
           
            # Write beats file
            write_beats_file(output_dir + song_name + ".beats", beats)

            print "Successfully downloaded {}".format(song_name)
            count+=1
            if count >= num_songs:
                break

        if count >= num_songs:
            break

if __name__ == '__main__':
    main()
