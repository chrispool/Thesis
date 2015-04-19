#!/usr/bin/python3

"""
##############
ClusterCreator
##############
Maakt candidate clusters gegeven de tweet dictionaries gegenereerd door de 
TweetPreprocessor. De clusters bestaan uit tweets die binnen een bepaalde 
geoHash en tijd zijn gepost.
"""

from collections import defaultdict

class ClusterCreator:
    
    def __init__(self, tweetDicts):
        # SETTINGS
        self.MINUTES = 60     # Na hoeveel minuten kan een tweet niet meer
                              # bij een event horen?
        
        # voor de keys van de tweet dictionaries, zie TweetPreprocessor.py
        self.tweetDicts = tweetDicts
        # maak nieuwe clusters
        self.clusters = defaultdict(self.__timeTweetDict)
        self.__createClusters()
        
    def getClusters(self):
        return self.clusters
            
    def __timeTweetDict(self):
        return defaultdict(list)

    def __createClusters(self):
        print("Creating candidate clusters...")
    
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
