#!/usr/bin/env python

import sys
import wavutil

def usage():
    print "python driver.py <dataset_directory>"

def main():
    dataset_dir = sys.argv[1]

    for w in wavutil.get_wav_files(dataset_dir):
        print w
        break


if __name__ == "__main__":
    main()
