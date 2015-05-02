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
        
        for h in self.candidates:
            for t in self.candidates[h]:
                candidate = self.candidates[h][t] 
                featuresCat = featureSelector.wordFeatureSelector(candidate)
                label = self.classifierCat.classify(featuresCat)
                #featuresBi = featureSelector.featureSelector(candidate,self.classifierCat)
        
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
        # (annotate a test set from april and find a way to test with ClassifierCreator?)
        #  1. Get features from the candidates: FeatureSelector (also use this for ClassifierCreator?)?
        #  2. Classify the feature sets generated by the FeatureSelector.
        #  3. Throw stuff in Google Map.
        
# DEMO
if __name__ == "__main__":
    detective = EventDetective2()