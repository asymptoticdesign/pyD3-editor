"""
Title: echonest
Author: nathan lachenmyer
Description: A python library that parses data acquired from echonest
Usage:
Date Started: 2012 Sept
Last Modified: 2012 Oct
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

def requestInfo(request, params={},baseurl='http://developer.echonest.com/api/v4/'):
    """
    Request data from the etsy server.  request is in the form of an URI as described by the etsy documentation; params is a dictionary of the format {'parameter':'value'}
    """
    paramString = formatParams(params)
    url = baseurl+request+paramString
    urlobj = urllib.urlopen(url)
    data = urlobj.read()
    parsedData = json.loads(data,object_hook=decode_dict)
    return parsedData

def formatKey(key, mode):
    """
    Format the key signature of the song based off of the key object from echonest.
    """
    keyIndex = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    returnString = keyIndex[key]
    if mode == 1:
        returnString = keyIndex[key] + 'm'
    return returnString

def findSongs(artistID):
    response = requestInfo('artist/songs',params={'api_key':apiKey,'id':artistID,'format':'json','start':'0'})
    return response

def getTrackProfile(trackID):
    response = requestInfo('song/profile',params={'api_key':apiKey,'id':artistID,'format':'json','id':trackID})
    return response

def findArtist(artist):
    response = requestInfo('artist/search',params={'api_key':apiKey,'format':'json','start':'0','name':artist})
    return response

#def uploadTrack(filePath):
    
