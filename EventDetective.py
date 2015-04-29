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
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from nltk.classify.scikitlearn import SklearnClassifier
import random
from modules import tabulate

class EventDetective:

    def __init__(self):
        self.dataSets = os.listdir('data/')
        self.idf = Counter()
        self.annotation = {}
        self.candidates = {}
        self.__loadDataSet()
        self.calculateIDF()
        self.classifyNLTK()
        self.generateMarkers()
    
    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        with open("data/" + self.dataSets[choice] + "/annotation_chris.json") as jsonFile:
            self.annotation = json.load(jsonFile)

        with open("data/" + self.dataSets[choice] + "/eventCandidates.json") as jsonFile:
            self.candidates = json.load(jsonFile)

    def calculateIDF(self):
        n = 0        
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                # een tweet is een document (niet een cluster)
                for tweet in self.candidates[geohash][timestamp]:
                    self.idf.update(set(tweet['tokens']))
                    n += 1
        for word in self.idf:
            self.idf[word] = log(n/self.idf[word])   
    
    def classifyNLTK(self):
        accuracy = 0
        baselineAvg = 0
        table = []
        for i in range(5):
            self.dataset = []
            for g in self.candidates:
                if g in self.annotation:
                    for t in self.candidates[g]:
                        if t in self.annotation[g]:
                            self.dataset.append( (self.featureSelector(self.candidates[g][t]), self.isEvent(g,t)  ))          
            
            random.shuffle(self.dataset) #shuffle dataset

            dataLen = len(self.dataset)
            trainSplit = int(0.8 * dataLen)
            train = self.dataset[:trainSplit] 
            test = self.dataset[trainSplit:]
            self.classifier = nltk.NaiveBayesClassifier.train(train)
            #self.classifier = nltk.MaxentClassifier.train(train)
            
            
            #print(self.classifier.show_most_informative_features(2))
            
            refsets = defaultdict(set)
            testsets = defaultdict(set)
            baseline = defaultdict(set)

            for n, (feats, label) in enumerate(test):
                refsets[label].add(n)
                observed = self.classifier.classify(feats)
                testsets[observed].add(n)
                baseline['event'].add(n)

            a = nltk.classify.accuracy(self.classifier,test)
            accuracy += a
            
            baseL = nltk.metrics.precision(refsets['event'], baseline['event']) #precision event
            baselineAvg += baseL
            
            pEvent = nltk.metrics.precision(refsets['event'], testsets['event']) #precision event
            rEvent = nltk.metrics.recall(refsets['event'], testsets['event']) #recall event
            fEvent = nltk.metrics.f_measure(refsets['event'], testsets['event']) #f score

            pNoEvent = nltk.metrics.precision(refsets['noEvent'], testsets['noEvent']) #precision no event
            rNoEvent = nltk.metrics.recall(refsets['noEvent'], testsets['noEvent']) #recall no event
            fNoEvent = nltk.metrics.f_measure(refsets['noEvent'], testsets['noEvent']) #f score no event

            table.append([i,round(baseL, 2), round(a, 2), round(pEvent,2), round(rEvent,2),round(fEvent,2),round(pNoEvent,2), round(rNoEvent,2), round(fNoEvent,2)])
            
        print (tabulate.tabulate(table, headers=['#', 'Baseline', 'Accuracy', 'Pre. Event','Rec. Event','F. Event','Pre. No-event','Rec. No-event','F. No_Event']))
        print("Avg accuracy = {}".format(round(accuracy / (i + 1) , 2)))
        print("Avg baseline accuracy (everything is an event)= {}".format(round(baselineAvg / (i + 1) , 2)))
        
    def featureSelector(self, cluster):
        featuresDict = {}
        #featuresDict['overlap'] = features.wordOverlap(cluster)
        #featuresDict['overlapSimple'] = features.wordOverlapSimple(cluster)
        featuresDict['overlapUser'] = features.wordOverlapUser(cluster)
        #featuresDict['nUsers'] = features.uniqueUsers(cluster)
        featuresDict['nTweets'] = features.nTweets(cluster)
        featuresDict['atRatio'] = features.atRatio(cluster) 
        featuresDict['overlapHashtags'] = features.overlapHashtags(cluster)
        #featuresDict['averageTfIdf'] = features.averageTfIdf(cluster, self.idf)

        return featuresDict


    def isEvent(self,geohash,timestamp):
        # waarden groter/kleiner dan 0 zijn True, gelijk aan 0 is False
        if self.annotation[geohash][timestamp]:
            return 'event'
        else:
            return 'noEvent'

    def generateMarkers(self):
        #generate markers True positives, true negatives, false positives and false negatives
        print("Creating Google Maps markers...")
        
        js = open('vis/map/events.js','w')
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
                features = self.featureSelector(self.candidates[geohash][timestamp])
                featureString = ''
                for key in features:
                    featureString += " {} - {} |".format(key, features[key])
                writableCluster += featureString
                # JS file maken voor Google maps
                result = self.classifier.classify(features)
                if result == 'event':
                    js.write("['{}', {}, {}, '{}', '{}'],".format(writableCluster, avgLat,avgLon, result,self.isEvent(geohash, timestamp)))
        js.write('];')
        js.close()



# DEMO
if __name__ == "__main__":
    detective = EventDetective()
