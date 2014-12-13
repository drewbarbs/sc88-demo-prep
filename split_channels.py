#!/usr/bin/env python3

"""
Prepare 32 channel Roland GS MIDI SC88 demo files for playback with aplaymidi
"""

__author__ = "Andrew Barbarello"
__license__ = "GPL"
__email__ = "drewbarbs91@gmail.com"

import re
import os
import sys
import struct
import traceback

def main(fbytes):
    m = re.search(rb"MThd\x00\x00\x00\x06(..)(..)..", fbytes)
    assert m
    out_bytes = m.group(0)
    midi_format, = struct.unpack('>H', m.group(1))
    num_tracks, = struct.unpack('>H', m.group(2))
    print('Parsing a Type-{} MIDI file with {} tracks.'.format(midi_format, num_tracks))
    assert midi_format == 1
    tracks = re.finditer(rb"MTrk(....).*?\xff\x2f\x00", fbytes, re.DOTALL)
    for i, track_match in enumerate(tracks):
        track_chunk = track_match.group(0)
        track_numbytes, = struct.unpack('>I', track_match.group(1))
        # Try to find track name event
        tname_index = track_chunk.find(b'\xff\x03')
        if tname_index > -1:
            tname_len = track_chunk[tname_index+2]
            tname_start = tname_index + 3
            tname_end = tname_start + tname_len
            tname = track_chunk[tname_start:tname_end]
            if i == 0:
                print('Midi song name:', tname.decode('ascii'))
                out_bytes += track_match.group(0)
                continue # type 1 midi file: first chunk has no note data
            if b'PartB' in tname:
                out_bytes += track_chunk[:4]
                # add the 4 track-length bytes, adjusted for added port-num meta event
                out_bytes += struct.pack('>I', track_numbytes + 4)
                # all midi events in this track will apply to port 1
                out_bytes += b'\x00\xff\x21\x01\x01'
                # append the rest of the track bytes
                out_bytes += track_chunk[8:]
            else: # this is a track with a name not containing PartB
                out_bytes += track_chunk
        else: # this is a track with no name
            out_bytes += track_chunk
    return out_bytes

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: split_channels <name_of_midi_file>')
        exit(0)
    fname = sys.argv[1]
    fname_wo_extension, extension = os.path.splitext(fname)
    try:
        with open(fname, 'rb') as f:
            fbytes = f.read()
            transformed = main(fbytes)
            with open(fname_wo_extension + '-split' + extension, 'wb') as f:
                f.write(transformed)
    except Exception as e:
        print("Couldn't read file:", file=sys.stderr)
        traceback.print_exc()
        exit(1)
