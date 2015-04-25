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


class EventDetective:

    def __init__(self):
        self.dataSets = os.listdir('data/')
        self.words = Counter()
        self.annotation = {}
        self.candidates = {}
        self.__loadDataSet()
        self.calculateIDF()
        self.classifyNLTK()
    
    
    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        #todo, wat als je verkeerde dataset opgeeft..		
        jsonFile =  open("data/" + self.dataSets[choice] + "/annotation.json")
        self.annotation = json.load(jsonFile)

        jsonFile =  open("data/" + self.dataSets[choice] + "/eventCandidates.json")
        self.candidates = json.load(jsonFile)

    def calculateIDF(self):
        n = 0        
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                for tweet in self.candidates[geohash][timestamp]:
                    self.words.update(set(tweet['tokens']))
                    n += 1
        for word in self.words:
            self.words[word] = log(n/self.words[word])   
    
    def classifyNLTK(self):
        accuracy = 0
        for i in range(10):
            self.dataset = []
            for g in self.candidates:
                if g in self.annotation:
                    for t in self.candidates[g]:
                        if t in self.annotation[g]:
                            self.dataset.append( (self.featureSelector(self.candidates[g][t]), self.isEvent(g,t)  ))
        
            train = self.dataset[:50]
            test = self.dataset[50:]
            classifier = nltk.NaiveBayesClassifier.train(train)
            #classifier = nltk.MaxentClassifier.train(train)
            #classifier = nltk.DecisionTreeClassifier.train(train)
            
            print(classifier.show_most_informative_features(10))
            
            refsets = defaultdict(set)
            testsets = defaultdict(set)

            for i, (feats, label) in enumerate(test):
                refsets[label].add(i)
                observed = classifier.classify(feats)
                testsets[observed].add(i)
            a = nltk.classify.accuracy(classifier,test)
            accuracy += a
            print("accuracy: {}".format(a))
            print()
            print ('Precision Event:', nltk.metrics.precision(refsets['event'], testsets['event']))
            print ('Recall Event:', nltk.metrics.recall(refsets['event'], testsets['event']))
            print ('F-measure Event:', nltk.metrics.f_measure(refsets['event'], testsets['event']))
            print()
            print ('Precision Non-event:', nltk.metrics.precision(refsets['noEvent'], testsets['noEvent']))
            print ('Recall Non-event:', nltk.metrics.recall(refsets['noEvent'], testsets['noEvent']))
            print ('F-measure Non-event:', nltk.metrics.f_measure(refsets['noEvent'], testsets['noEvent']))

        print(accuracy / 10)
    
    def featureSelector(self, cluster):
        featuresDict = {}
        featuresDict['overlap'] = features.wordOverlap(cluster)
        featuresDict['nUsers'] = features.uniqueUsers(cluster)
        featuresDict['nTweets'] = features.nTweets(cluster) #zonder deze feature presteert de classifier beter...
        featuresDict['atRatio'] = features.atRatio(cluster) 
        featuresDict['overlapHashtags'] = features.overlapHashtags(cluster) 

        return featuresDict


    def isEvent(self,geohash,timestamp):
        if self.annotation[geohash][timestamp] > 0:
            return 'event'
        else:
            return 'noEvent'

    

# DEMO
if __name__ == "__main__":
    detective = EventDetective()