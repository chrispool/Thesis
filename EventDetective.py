#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""

import os, sys, json, pickle
from collections import defaultdict, Counter
import nltk
from math import log, log2
from sklearn.naive_bayes import MultinomialNB
from nltk.classify.scikitlearn import SklearnClassifier
import random
from modules import tabulate
from FeatureSelector import FeatureSelector
from Wikification import Wikification
from operator import itemgetter

class EventDetective:

    def __init__(self):
        self.dataSets = os.listdir('data/')
        self.candidates = {}
        self._loadDataSet()
        featureSelector = FeatureSelector(self.candidates)
        #self.featuresCat = []
        #self.featuresBi = []
        self.events = []
        
        # detecteer events
        for h in self.candidates:
            for t in self.candidates[h]:
                candidate = self.candidates[h][t] 
                featuresCat = featureSelector.getFeatures(candidate, ['wordFeatures'])
                featureSelector.addCategoryClassifier(self.classifierCat)
                label = self.classifierCat.classify(featuresCat)
                featuresBi = featureSelector.getFeatures(candidate,['category', 'wordOverlapUser'])
                if self.classifierBi.classify(featuresBi) != "geen_event":
                    self.events.append((candidate,label))                          
        
        self.wiki = Wikification(self.events) #adds wikification to events
        self._generateMarkers()
        
    def _loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select a dataset with classifiers: "))
        
        with open("data/" + self.dataSets[choice] + "/categoryClassifier.bin", 'rb') as binFile:
            self.classifierCat = pickle.load(binFile)

        with open("data/" + self.dataSets[choice] + "/eventClassifier.bin", 'rb') as binFile:
            self.classifierBi = pickle.load(binFile)
        
        choice = int(input("Select a dataset with event candidates that need event detection: "))

        with open("data/" + self.dataSets[choice] + "/eventCandidates.json") as jsonFile:
            self.candidates = json.load(jsonFile)
        
        # TODO 
        # 1. Annotate a test set from april (or last year?) and find a way to test with ClassifierCreator
        
    def _generateMarkers(self):
        print("Creating Google Maps markers & add WIKI links...")
        
        js = open('vis/map/js/markers.js','w')
        js.write('var locations = [')

        events = self.wiki.getWiki()
        
        for tweets,label,ngrams in events:
            writableCluster = ''
            gh = []
            i = 0
            avgLon = 0
            avgLat = 0
            #tweets = sorted(tweets, key=itemgetter('unixTime'));
                              
            for tweet in tweets:
                i = i + 1
                gh.append(tweet['geoHash'])
                avgLon += float(tweet["lon"])
                avgLat += float(tweet["lat"])
                # backslashes voor multiline strings in Javascript
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text']).replace("'", "\\'")
            # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
            # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
            # Oftewel, we doen even alsof de aarde plat is ;-)
            avgLon /= i
            avgLat /= i
            writableCluster += "</br>" + str(ngrams).replace("'", "\\'")
            js.write("['{}', {}, {}, '{}'],".format(writableCluster,avgLat,avgLon,label))
        js.write('];')
        js.close()
        
# DEMO
if __name__ == "__main__":
    detective = EventDetective()