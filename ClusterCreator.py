#!/usr/bin/python3

"""
##############
ClusterCreator
##############
Maakt event candidate clusters, gegeven een .txt-bestand met tweets 
in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

De clusters bestaan uit tweets die binnen een bepaalde geoHash en 
tijd zijn gepost.
"""

import os, sys, time
from TweetPreprocessor import TweetPreprocessor
from collections import defaultdict

class ClusterCreator:
    
    def __init__(self, tweetFile):
        # SETTINGS
        self.MINUTES = 60     # Na hoeveel minuten kan een tweet niet meer
                              # bij een event horen?
        self.N_TWEETS = 2     # Min hoeveelheid tweets in candidate cluster
        self.UNIQUEUSERS = 2     # Min hoeveelheid tweets in candidate cluster
        
        preprocess = TweetPreprocessor(tweetFile)
        # voor de keys van de tweet dictionaries, zie TweetPreprocessor.py
        self.tweetDicts = preprocess.getTweetDicts()
        self.idf = preprocess.getIdf()
        # maak nieuwe clusters
        self.clusters = defaultdict(self.__timeTweetDict)
        self.__createClusters()
        
    def getClusters(self):
        return self.clusters
    
    def getIdf(self):
        return self.idf
            
    def __timeTweetDict(self):
        return defaultdict(list)
            
    def __createClusters(self):
        print("Creating tweet clusters...")
    
        for tweet in self.tweetDicts:
            geoHash = tweet["geoHash"]
            tweetTime = tweet["unixTime"]
            foundTime = tweetTime

            if geoHash in self.clusters:
                for times in self.clusters[geoHash].keys():
                    if times <= tweetTime <= times + self.MINUTES * 60:
                        foundTime = times
            
            self.clusters[geoHash][foundTime].append(tweet)
            if tweetTime != foundTime:
                # zet de tijd vooruit naar de tijd van de nieuwe tweet
                # om het event in leven te houden
                self.clusters[geoHash][tweetTime] = self.clusters[geoHash][foundTime]
                # verwijder de cluster op de oude tijd
                del self.clusters[geoHash][foundTime]

# DEMO
if __name__ == "__main__":
    start = time.time() 
    if len(sys.argv) != 2:
        print("./ClusterCreator.py tweetFile")
        sys.exit()
    creator = ClusterCreator(sys.argv[1])
    runTime = time.time() - start
    print("Finding clusters and selecting event candidates took", runTime, "seconds.")