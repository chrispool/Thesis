#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""
import os, sys, msgpack, time, json
from collections import defaultdict, Counter
import nltk
from nltk.stem.snowball import SnowballStemmer
from math import log2
class EventDetective:

    def __init__(self):
        #self.__emptyClusterFolder()
        self.stemmer = SnowballStemmer("dutch", ignore_stopwords=True)
        self.words = Counter()
        self.dataSets = os.listdir('data/')
        self.annotation = {}
        self.candidates = {}
        self.__loadDataSet()
        self.calculateIDF()
        self.classifyEvents()
        #self.selectEvents()
    
    def eventDic(self):
        return defaultdict(list)    

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
            self.words[word] = log2(n/self.words[word])   
    
    def classifyEvents(self):
        self.value = 4.5

            
        self.events = defaultdict(self.eventDic)
        self.noevents = defaultdict(self.eventDic)
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                if self.featureWordOverlap(self.candidates[geohash][timestamp]) >= self.value:
                    self.events[geohash][timestamp] = self.candidates[geohash][timestamp]
                else:
                    self.noevents[geohash][timestamp] = self.candidates[geohash][timestamp]
        self.calculatePrecisionRecall()


    def generateGoogleMap(self):
        pass

    def calculatePrecisionRecall(self):
        tp = 0 #true positive
        fp = 0 #false positive
        tn = 0 #true negative
        fn = 0 #false negative

        for geohash in self.events:
            if geohash in self.annotation:
                for timestamp in self.events[geohash]:
                    if timestamp in self.annotation[geohash]:
                        if self.annotation[geohash][timestamp] > 0: #goed geclassificeerd
                            tp += 1
                        else:
                            fp += 1
                            self.printTweets(self.events[geohash][timestamp], 'False positive')
                    
        for geohash in self.noevents:
            if geohash in self.annotation:
                for timestamp in self.noevents[geohash]:
                    if timestamp in self.annotation[geohash]:
                        if self.annotation[geohash][timestamp] == 0: #goed geclassificeerd
                            tn += 1
                        else:
                            fn += 1
                            self.printTweets(self.noevents[geohash][timestamp], 'False negative')

        nDoc = tp+fp+tn+fn
        precision = tp / (tp + fp)  #fraction of retrieved documents that are relevant
        recall = tp / (tp + fn)
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        fscore = 2 * ((precision * recall)/(precision + recall))
        print("Value = {:.1f}, Precision: {:.2f} Recall: {:.2f} accuracy: {:.2f} fscore: {:.2f}".format(self.value, precision, recall, accuracy, fscore))

       
    def printTweets(self, cluster, message):
        print()
        print("<------{}-------->".format(message))
        for tweet in cluster:
            print(tweet['text'])
        print()


    def featureWordOverlap(self, candidate):
        words = Counter()
        n = len(candidate)
        for row in candidate:    
            words.update(set(row['tokens']))  
        for word in words:
            words[word] = (words[word] - 1) * self.words[word] #dat het voor komt in de eigen tweet is niet relevant
        
        return sum(words.values()) / n

    def selectEvents(self):
        n = 21
        print("\n### A selection of", n, "detected events ###\n")
        count = 0
        for geoHash in self.candidates:
            for times in self.candidates[geoHash]:
                for tweet in self.candidates[geoHash][times]:
                   print(tweet["localTime"], tweet["user"], tweet["text"])
            print()
            count += 1
            if count == 10:
                break

# DEMO
if __name__ == "__main__":
    detective = EventDetective()