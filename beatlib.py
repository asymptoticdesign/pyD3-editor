"""
Title: beatport
Author: nathan lachenmyer
Description: A python library that parses data acquired from echonest
Usage:
Date Started: 2012 Nov
Last Modified: 2012 Nov
"""

import sys
import urllib
import json
import urlparse
import re

def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv
        
def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv

def formatParams(paramDictionary):
    """
    Formats a dictionary to the appropriate http query format.
    """
    paramString = '?'
    for key in paramDictionary.keys():
        paramString += '&' + key + '=' + paramDictionary[key]
    return paramString

def requestInfo(request, params={},baseurl='http://api.beatport.com/'):
    """
    Request data from the server.  request is in the form of an URI; params is a dictionary of the format {'parameter':'value'}
    """
    paramString = formatParams(params)
    url = baseurl+request+paramString
    urlobj = urllib.urlopen(url)
    data = urlobj.read()
    parsedData = json.loads(data,object_hook=decode_dict)
    return parsedData

def formatKey(keyDict):
    """
    Format the key signature of the song based off of the key object from beatport.
    """
    returnString = keyDict['standard']['letter']
    if keyDict['standard']['chord'] == 'minor':
        returnString + 'm'
    if keyDict['standard']['sharp']:
        returnString + '#'
    if keyDict['standard']['flat']:
        returnString + 'b'
    return returnString
        
def getTrackData(trackID):
    """
    Given a trackID and artistID, returns relevant information for correcting an id3tag
    """
    response = requestInfo('catalog/tracks',params={'format':'json','id':trackID})
    data = {'title' : response['results'][0]['title'],
            'artist' : response['results'][0]['artists'][0]['name'],
            'length' : response['results'][0]['length'],
            'key' : formatKey(response['results'][0]['key']),
            'bpm' : response['results'][0]['bpm'],
            'label' : response['results'][0]['label']['name']
            }
    return data

def artistSearch(artistName):
    response = requestInfo('catalog/search',params={'query':artistName,'format':'json','facets':'fieldType:performer'})
    for artist in response['results']:
        print 'Artist Name: ' + artist['name']
        print 'Artist ID: ' + str(artist['id'])
        genreString = ''
        for genre in artist['genres']:
            genreString += genre['name'] + ' / '
        print 'Genres: ' + genreString[:-3]
        print '' #newline
    return response['results']

def trackSearch(trackName,artistName):
    response = requestInfo('catalog/search',params={'query':trackName,'format':'json','facets':'fieldType:track','facets':'performerName:'+artistName})
    for track in response['results']:
        print 'Track Name: ' + track['title']
        print 'Track ID: ' + str(track['id'])
        artistString = ''
        for artist in track['artists']:
            artistString += artist['name'] + ' / '
        print 'Artists: ' + artistString[:-3]
        print 'Label: ' + track['label']['name'] + " (" + track['releaseDate'][:4] + ")"
        print '' #newline
    return response['results']
