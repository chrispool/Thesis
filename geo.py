#!/usr/bin/python3

import sys
import geohash
from collections import defaultdict
from collections import Counter
import math
import time
import datetime
from operator import itemgetter
import os

# SETTINGS
MINUTES       = 60  # maximum tijdsinterval tweets binnen een GeoHash
N_TWEETS      = 2   # minimale hoeveelheid tweets in cluster
HASH_ACCURACY = 7   # nauwkeurigheid van GeoHash
UNIQUEUSERS   = 3   # aantal unieke gebruikers in cluster
UNIQUECOORDS  = 3   # aantal unieke locaties in cluster

def timeTweetDict():
    return defaultdict(list)

def emptyClusterFolder():
	filelist = [ f for f in os.listdir("clusters/") if f.endswith(".txt") ]
	for f in filelist:
		os.remove('clusters/' + f)
	print("cluster folder is empty")

def createClusters(tweetfile):
    print("Finding tweet clusters...")
    
    clusters = defaultdict(timeTweetDict)
    
    with open(tweetfile) as f:
        for line in f:
            tweet = line.strip().split('\t')
            coord = tweet[1].split()
            
            geoHash = geohash.encode(float(coord[1]),float(coord[0]), HASH_ACCURACY)
            tweetTime = ' '.join(tweet[3].split()[:2])
            # converteer de tijd van de tweet naar unix time
            unixTime = int(time.mktime(datetime.datetime.strptime(tweetTime, "%Y-%m-%d %H:%M:%S").timetuple()))
            
            foundTime = unixTime
            # probeer geohash en tijd toe te voegen aan bestaande cluster
            if geoHash in clusters:
                for times in clusters[geoHash]:
                    if times <= unixTime <= times + MINUTES * 60:
                        # wat nu als deze tweet binnen de tijd van meerdere clusters valt?
                        # ik ga hier uit van de laatst geziene tijd
                        foundTime = times
            
            clusters[geoHash][foundTime].append(tweet)

    return clusters
    
    
def selectEventCandidates(clusters):
    print("Selecting event candidates...")
    
    js = open('markers.js','w')
    js.write('var locations = [')
    i = 1
    
    # loop door clusters om te kijken wat event candidates zijn
    for hashes in clusters:
        for times in clusters[hashes]:
            
            tweets = clusters[hashes][times]
            
            userlist = []
            geolist = []

            # cluster bevat meer dan N_TWEETS
            if len(tweets) > N_TWEETS:
                for tweet in tweets:
                    if not tweet[2] in userlist:  # toevoegen aan lijst met unieke users van dit cluster
                        userlist.append(tweet[2])
                    if not tweet[1] in geolist:   # toevoegen aan lijst met unieke locaties van dit cluster
                        geolist.append(tweet[1])
    
            # cluster pas opslaan wanneer er meer dan 1 unieke gebruiker en locatie in staat
            if len(userlist) >= UNIQUEUSERS and len(geolist) >= UNIQUECOORDS:
                with open('clusters/' + hashes + '-' + str(times) + '.txt','w') as f:
                    for tweet in tweets:
                        i = i + 1
                        coord = tweet[1].split()
                        # textfiles maken van alle afzonderlijke clusters en JS file maken voor Google maps
                        
                        f.write("{}, {}, {}, {} \n".format(tweet[2], tweet[0].replace("'", ""),
                                                           ', '.join(reversed(coord)), tweet[3]))
                        js.write("['{} {} {}', {}, {}],\n".format(tweet[2],tweet[3], tweet[0].replace("'", ""), 
                                                                  ', '.join(reversed(coord)), i))
                        
    js.write('];')
    js.close()          


if __name__ == "__main__":
    start = time.time()
    emptyClusterFolder()
    clusters = createClusters(sys.argv[1])
    selectEventCandidates(clusters)
    runTime = time.time() - start
    print("Finding clusters and selecting event candidates took", runTime, "seconds.")