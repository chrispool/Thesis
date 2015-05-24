#!/usr/bin/python3

"""
#################
ClassifierCreator
#################
Creates category & event/no-event classifier given a dataset
"""

import os, sys, json, pickle
from collections import defaultdict, Counter
import nltk
from math import log, log2
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.linear_model import SGDClassifier
from nltk.classify.scikitlearn import SklearnClassifier
import random
from modules import tabulate
from FeatureSelector import FeatureSelector

class ClassifierCreator:

    def __init__(self):

        
        self.dataSets = os.listdir('data/')
        self.categories = ["geen_event", "sport","entertainment", "bijeenkomst", "incident", "anders"]
        self.classifierAFeatures = ['wordFeatures']
        self.classifierBFeatures =  ['category', 'location','wordOverlapSimple','wordOverlapUser']
        self.annotation = {}
        self.candidates = {}
        self.result = defaultdict(self.resultDictionary)
        self.cm = []
        self.informativeFeatures = []
        self.accuracy  = []
        self.choice = 0
        
        # real test or dev test?
        self.realTest = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "-test":
                self.realTest = True
        
        if self.realTest:
            print("\nThe system is running in TEST mode.\n")
            self.ITERATIONS = 1
        else:
            print("\nThe system is running in DEVTEST mode.\n")
            self.ITERATIONS = 10
        


        self.__loadDataSet()
        self.featureSelector = FeatureSelector(self.candidates)
        self._trainClassifiers()
        #self._saveClassifiers()

    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        if self.realTest:
            self.choice = int(input("\nPlease select an annotated TRAIN dataset: "))
        else:
            self.choice = int(input("\nPlease select an annotated TRAIN/DEVTEST dataset: "))
        
        with open("data/" + self.dataSets[self.choice] + "/sanitizedAnnotation.json") as jsonFile:
            self.annotation = json.load(jsonFile)

        with open("data/" + self.dataSets[self.choice] + "/sanitizedEventCandidates.json") as jsonFile:
            self.candidates = json.load(jsonFile)
         
        if self.realTest:
            print()
            for i, dataset in enumerate(self.dataSets):
                print("{}: {}".format(i, dataset))
            choice = int(input("\nPlease select an annotated TEST dataset: "))
                
            with open("data/" + self.dataSets[choice] + "/sanitizedEventCandidates.json") as jsonFile:
                self.testCandidates = json.load(jsonFile)

            #add to annotation file
            with open("data/" + self.dataSets[choice] + "/sanitizedAnnotation.json") as jsonFile:
                self.testAnnotation = json.load(jsonFile)

    def _saveClassifiers(self):
        print("\nSaving the category and event classifier...")
        
        with open("data/" + self.dataSets[self.choice] + "/categoryClassifier.bin", "wb") as f:
            pickle.dump(self.classifierA,f)
            
        with open("data/" + self.dataSets[self.choice] + "/eventClassifier.bin", "wb") as f:
            pickle.dump(self.classifierB,f)
    
    def _selectDataset(self):
        dataset = []
        for h in self.candidates:
            for t in self.candidates[h]:
                dataset.append( (self.candidates[h][t], self.eventType(h,t) ) )
                
        if self.realTest:
            # use all of the annotated train data to train
            self.trainData = dataset
            
            dataset = []
            for h in self.testCandidates:
                for t in self.testCandidates[h]:
                    dataset.append( (self.testCandidates[h][t], self.eventType(h,t) ) )
                    
            self.testData = dataset
        else:
            random.shuffle(dataset)
            # random dataset splits for cross validation
            trainSplit = int(0.8 * len(dataset))
            self.trainData = dataset[:trainSplit]
            self.testData = dataset[trainSplit:]
        
    def _trainClassifiers(self):
        print("\nClassifying events...\n")
        for i in range(self.ITERATIONS):
            if self.realTest:
                testMode = "TEST"
            else:
                testMode = "DEVTEST"
            print("###########")
            print("### {} {}".format(testMode,i+1))
            print("#############")
            self._selectDataset()
            self.testA = []
            self.trainA = []
            self.testB = []
            self.trainB = []
           
            #first train category classifier
            print("### TRAINING STEP 1: Training category classifier (Naive Bayes with word features) ###")
            for candidate, label in self.testData:
                featuresA = self.featureSelector.getFeatures(candidate, self.classifierAFeatures)
                self.testA.append((featuresA, label))         
            
            for candidate, label in self.trainData:
                featuresA = self.featureSelector.getFeatures(candidate, self.classifierAFeatures)
                self.trainA.append((featuresA, label))

            # MultinomialNB lijkt hier net zo goed als de nltk naive bayes classifier, maar is wel wat sneller
            self.classifierA = SklearnClassifier(MultinomialNB()).train(self.trainA)
            # sends the category classifier to the featureSelector
            self.featureSelector.addCategoryClassifier(self.classifierA)
                
            print("### TRAINING STEP 2: Training event/non-event classifier (Naive Bayes with category & other features) ###")
            # second step train the event/no event classifier
            for candidate, label in self.testData:
                featuresB = self.featureSelector.getFeatures(candidate, self.classifierBFeatures )   
                self.featureKeys = featuresB.keys()
                self.testB.append((featuresB, label)) 
            
            for candidate, label in self.trainData:
                featuresB = self.featureSelector.getFeatures(candidate, self.classifierBFeatures)
                self.featureKeys = featuresB.keys()
                self.trainB.append((featuresB, label))

            self.classifierB = nltk.SklearnClassifier(MultinomialNB()).train(self.trainB)

            self.calculateStats(i)
            
        self.printStats()

    def resultDictionary(self):
        return defaultdict(list)

    def calculateStats(self, i):
        '''Function to calculate all stats'''
        #calculate cm for this iteration
        ref = []
        tagged =[]
        for f, e in self.testB:
            ref.append(self.classifierB.classify(f))
            tagged.append(e)

        self.cm.append(nltk.ConfusionMatrix(ref, tagged))
        #self.informativeFeatures.append(self.classifierB.most_informative_features(10))
        print()
        #calculate precision and recall for this iteration for each category
        refsets = defaultdict(set)
        testsets = defaultdict(set)

        for n, (feats, label) in enumerate(self.testB):
            refsets[label].add(n)
            observed = self.classifierB.classify(feats)
            testsets[observed].add(n)

        self.accuracy.append(nltk.classify.accuracy(self.classifierB,self.testB))
        
        #for elke category precision and recall berekenen.
        for category in self.categories:
            if category in testsets:
                self.result[category]["p"].append(nltk.metrics.precision(refsets[category], testsets[category]))
                self.result[category]["r"].append(nltk.metrics.recall(refsets[category], testsets[category]))
                self.result[category]["f"].append(nltk.metrics.f_measure(refsets[category], testsets[category]))
            else:
                self.result[category]["p"].append(float(0))
                self.result[category]["r"].append(float(0))
                self.result[category]["f"].append(float(0))

    def eventType(self,geohash,timestamp):
        # return values {strings gebruiken?}
        eventTypes = {0:"geen_event", 1:"sport", 2:"entertainment", 3:"bijeenkomst", 4:"incident", 5:"anders"}
        try:          
            returnValue  = eventTypes[self.annotation[geohash][timestamp]]
        except KeyError:
            returnValue  = eventTypes[self.testAnnotation[geohash][timestamp]]

        return returnValue

    def printStats(self):
        print(", ".join(self.classifierBFeatures))
        it = self.ITERATIONS
        print("### EVALUATION STEP 1: Detailed statistics for the classifier:")
        for i in range(it):
            if self.realTest:
                testMode = "TEST"
            else:
                testMode = "DEVTEST"
            print("\n###########")    
            print("### {} {}".format(testMode,i+1))
            print("#############\n")
            print(self.cm[i])
            print("Most informative features")
           # print(self.informativeFeatures[i])
        print("\n### EVALUATION STEP 2: Classification using features: {} | training set size: {} & test set size: {}\n".format(", ".join(self.featureKeys),len(self.trainB), len(self.testB)))
        headers = ['#', 'accuracy'] + self.categories
        
        prf = "P    R    F"
        table = [ ['', '', prf, prf,prf,prf,prf,prf]]
        for i in range(it):
            row = [i + 1, round(self.accuracy[i],2)]
            for category in self.categories:
                value = "{:.2f} {:.2f} {:.2f}".format(self.customRound(self.result[category]["p"][i],2), self.customRound(self.result[category]["r"][i],2), self.customRound(self.result[category]["f"][i],2))
                row.extend( [value] )
            table.append(row)
        
        #averages
        row = ["Avg.", round(sum(self.accuracy) / len(self.accuracy),2)]
        for category in self.categories:
            value = "{:.2f} {:.2f} {:.2f}".format(self.customAvg(self.result[category]["p"]), self.customAvg(self.result[category]["r"]), self.customAvg(self.result[category]["f"]))
            row.extend( [value] )
        table.append(row)

        print(tabulate.tabulate(table, headers=headers))
        print("\nLATEX table\n")
        print(tabulate.tabulate(table, headers=headers, tablefmt="latex"))

    def customAvg(self, l):
        try:
            returnValue = round(sum(l) / len(l),2)
        except TypeError:
            returnValue = 0.0
        return returnValue

    def customRound(self,n, d):
        try:
            returnValue = round(n,d)
        except TypeError:
            returnValue = 0.0

        return returnValue

# DEMO
if __name__ == "__main__":
    classifierCreator = ClassifierCreator()