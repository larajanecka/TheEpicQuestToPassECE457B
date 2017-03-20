from gmusicapi import Mobileclient
from gmusicapi import Webclient
import json
import os
import sys
import urllib2
import hdf5

# This program 



# A wrapper class allowing you to download songs from GooglePlayMusic
class GMSongClient():

    # Extract Google Auth credentials from the environment
    def __init__(self):
        email = os.environ['EMAIL']
        pw = os.environ['PASSWORD']
        self.api = Mobileclient()
        self.api.login(email, pw, Mobileclient.FROM_MAC_ADDRESS, 'en_us')

    def download_song(self, artist, title):
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
            print 'Unable to find song'
            return

        # Extract mp3 url
        store_id = song['track']['storeId']
        song_id = self.api.add_store_track(store_id)
        url = self.api.get_stream_url(song_id)

        # Download mp3 file
        mp3file = urllib2.urlopen(url)
        file_name = '{}.mp3'.format(query)
        with open(query,'wb') as output:
            output.write(mp3file.read())

#c = GMSongClient()
#c.download_song('Blink-182', 'What\'s My Age Again?')

def usage():
    print "usage: python generate_dataset.py <root_dir_of_hdf5_files> <output_directory> <#_of_songs_to_extract>"

def main():
    count = 0
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)

    data_dir = sys.argv[1]
    output_dir = sys.argv[2]
    num_songs = int(sys.argv[3])

    for root, dirs, files in os.walk(data_dir):
        for f in files:
            print f
            count+=1
            if count > 50:
                break
        if count > 50:
            break

if __name__ == '__main__':
    main()
