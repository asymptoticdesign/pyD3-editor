#!/usr/bin/env python
"""
Title: echolib
Author: nathan lachenmyer
Description: A python library that parses data acquired from echolib
Usage:
Date Started: 2012 Sept
Last Modified: 2012 Oct
"""

import sys
import os
import urllib
import json
import subprocess
import urlparse
import re
import echolib
import mutagen
from mutagen.id3 import *

echonestKey = 'C72STF6Q4CUNRUTUL'
_codegen_path = "ENMFP_codegen/codegen.Linux-i686"

def codegen(filename, start=10, duration=30):
    """ runs codegen on the given file, returns a tuple with
    the track id, a code string for lookup, and a codegen
    block for ingest
    """
    
    if not os.path.exists(_codegen_path):
        raise Exception("Codegen binary not found.")
    
    command = _codegen_path + " \"" + filename + "\" "
    if start >= 0:
        command = command + str(start) + " "
    if duration >= 0:
        command = command + str(duration)
        
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (jsonOutput, errs) = p.communicate()
    
    return jsonOutput

def unpackData(codegenOutput):
    JSON = json.loads(codegenOutput)[0]

    fingerprint = JSON['code']
    
    trackArtist = JSON['metadata']['artist']
    trackTitle = JSON['metadata']['title']
    trackGenre = JSON['metadata']['genre']
    trackAlbum = JSON['metadata']['release']
    return fingerprint

def formatMetadata(metadataString):
    metadataDict = {}
    metadataDict['title'] = metadataString['title']
    metadataDict['artist'] = metadataString['artist_name']
    metadataDict['bpm'] = str(int(metadataString['audio_summary']['tempo']))
    metadataDict['duration'] = str(int(metadataString['audio_summary']['duration']*1000))
    mode = metadataString['audio_summary']['mode']
    key = metadataString['audio_summary']['key']
    metadataDict['key'] = echolib.formatKey(key,mode)
    print metadataDict
    return metadataDict

def writeID3(filename,metadataDict):
    track = mutagen.id3.ID3(filename)
    print "Opened up file . . ."
    print "Current ID3 Tags:"
    print track.pprint()
    print "Fixing ID3 Tags . . ."
    track.add(mutagen.id3.TIT2(encoding = 3, text = metadataDict['title']))
    track.add(mutagen.id3.TPE1(encoding = 3, text = metadataDict['artist']))
    track.add(mutagen.id3.TBPM(encoding = 3, text = metadataDict['bpm']))
    track.add(mutagen.id3.TKEY(encoding = 3, text = metadataDict['key']))
    track.add(mutagen.id3.TLEN(encoding = 3, text = metadataDict['duration']))
    print "Success!"
    track.save()

output = codegen(sys.argv[1], start=0, duration=60)
audioFingerprint = unpackData(output)
response = echolib.requestInfo('song/identify',params={'api_key':echonestKey,'code':audioFingerprint,'bucket':'audio_summary'})
rawMetadata = response['response']['songs'][0]
metadata = formatMetadata(rawMetadata)
writeID3(sys.argv[1],metadata)
