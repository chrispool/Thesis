#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""
import features
import os, sys, json
from collections import defaultdict, Counter
import nltk
from math import log, log2
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.linear_model import SGDClassifier
from nltk.classify.scikitlearn import SklearnClassifier
import random
from modules import tabulate

class EventDetective:

    def __init__(self):
        #self.dataSets = os.listdir('data/')
        #self.annotation = {}
        #self.candidates = {}
        #self.__loadDataSet()

        #self.generateMarkers()
    """
    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        with open("data/" + self.dataSets[choice] + "/sanitizedAnnotation.json") as jsonFile:
            self.annotation = json.load(jsonFile)

        with open("data/" + self.dataSets[choice] + "/sanitizedEventCandidates_cleaned.json") as jsonFile:
            self.candidates = json.load(jsonFile)

    def eventType(self,geohash,timestamp):
        # return values {strings gebruiken?}
        eventTypes = {0:"geen event", 1:"sport", 2:"entertainment", 3:"bijeenkomst", 4:"incident", 5:"anders"}
         
        return eventTypes[self.annotation[geohash][timestamp]]
        
    def isEvent(self,geohash,timestamp):
        # waarden groter/kleiner dan 0 zijn True, gelijk aan 0 is False
        if self.annotation[geohash][timestamp]:
            return 'event'
        else:
            return 'noEvent'

    def generateMarkers(self):
        #generate markers True positives, true negatives, false positives and false negatives
        print("Creating Google Maps markers...")
        
        js = open('vis/map/markers.js','w')
        js.write('var locations = [')

        # loop door clusters om te kijken wat event candidates zijn
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:   
                tweets = self.candidates[geohash][timestamp]
                
                writableCluster = ''
                gh = []
                i = 0
                avgLon = 0
                avgLat = 0
                              
                for tweet in tweets:
                    i = i + 1
                    gh.append(tweet['geoHash'])
                    avgLon += float(tweet["lon"])
                    avgLat += float(tweet["lat"])
                    # backslashes voor multiline strings in Javascript
                    writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text'].replace("'", "\\'"))
                # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
                # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
                # Oftewel, we doen even alsof de aarde plat is ;-)
                
                avgLon /= i
                avgLat /= i
                #features = self.featureSelector(self.candidates[geohash][timestamp])
                #featureString = ''
                #for key in features:
                #    featureString += " {} - {} |".format(key, features[key])
                #writableCluster += featureString
                # JS file maken voor Google maps
                #result = self.classifierBi.classify(features)
                #if result == 'event':
                #    js.write("['{}', {}, {}, '{}', '{}'],".format(writableCluster, avgLat,avgLon, result,self.isEvent(geohash, timestamp)))
        js.write('];')
        js.close()"""

# DEMO
if __name__ == "__main__":
    detective = EventDetective()