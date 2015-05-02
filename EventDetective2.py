#!/usr/bin/python3

"""
##############
EventDetective2
##############
Detecteert events gegeven dataset
"""
import features
import os, sys, json, pickle
from collections import defaultdict, Counter
import nltk
from math import log, log2
from sklearn.naive_bayes import MultinomialNB
from nltk.classify.scikitlearn import SklearnClassifier
import random
from modules import tabulate
from FeatureSelector import FeatureSelector

class EventDetective2:

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
                featuresCat = featureSelector.wordFeatureSelector(candidate)
                label = self.classifierCat.classify(featuresCat)
                featuresBi = featureSelector.featureSelector(candidate,self.classifierCat)
                if self.classifierBi.classify(featuresBi) == "event":
                    self.events.append((candidate,label))
                    
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
        # 2. Throw stuff in Google Map.
        
    def _generateMarkers(self):
        #generate markers True positives, true negatives, false positives and false negatives
        print("Creating Google Maps markers...")
        
        js = open('vis/map/markers.js','w')
        js.write('var locations = [')

        for tweets,label in self.events:
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
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text']).replace("'", "\\'").replace("\\","\\\\")
                # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
                # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
                # Oftewel, we doen even alsof de aarde plat is ;-)
                avgLon /= i
                avgLat /= i
            js.write("['{}', {}, {}, '{}'],".format(writableCluster, avgLat,avgLon,label))
        js.write('];')
        js.close()
        
# DEMO
if __name__ == "__main__":
    detective = EventDetective2()