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
        self.ITERATIONS = 5
        self.dataSets = os.listdir('data/')
        self.categories = ["geen_event", "sport","entertainment", "bijeenkomst", "incident", "anders"]
        self.annotation = {}
        self.candidates = {}
        self.result = defaultdict(self.resultDictionary)
        self.cm = []
        self.mostInformativeBi = []
        self.mostInformativeCat = []
        self.acc  = 0
        self.baselineBi = 0
        self.choice = 0
        
        # real test or dev test?
        self.realTest = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "-test":
                self.realTest = True
        
        if self.realTest:
            print("\nThe system is running in TEST mode.\n")
        else:
            print("\nThe system is running in DEVTEST mode.\n")
        
        self.__loadDataSet()
        self.featureSelector = FeatureSelector(self.candidates)
        self._trainClassifiers()
        #self._saveClassifiers()

    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        self.choice = int(input("Select dataset: "))
        
        with open("data/" + self.dataSets[self.choice] + "/sanitizedAnnotation.json") as jsonFile:
            self.annotation = json.load(jsonFile)

        with open("data/" + self.dataSets[self.choice] + "/sanitizedEventCandidates_cleaned.json") as jsonFile:
            self.candidates = json.load(jsonFile)
         
        if self.realTest:
            print()
            for i, dataset in enumerate(self.dataSets):
                print("{}: {}".format(i, dataset))
            choice = int(input("Please select an annotated test dataset: "))
                
            with open("data/" + self.dataSets[choice] + "/sanitizedEventCandidates_cleaned.json") as jsonFile:
                self.testCandidates = json.load(jsonFile)

    def _saveClassifiers(self):
        print("Saving the category and event classifier...")
        
        with open("data/" + self.dataSets[self.choice] + "/categoryClassifier.bin", "wb") as f:
            pickle.dump(self.classifierCat,f)
            
        with open("data/" + self.dataSets[self.choice] + "/eventClassifier.bin", "wb") as f:
            pickle.dump(self.classifierBi,f)
    
    def _selectDataset(self):
        dataset = []
        for h in self.candidates:
            for t in self.candidates[h]:
                dataset.append( (self.candidates[h][t],self.isEvent(h,t), self.eventType(h,t) ) )
                
        if self.realTest:
            # use all of the annotated train data to train
            self.trainData = dataset
            
            dataset = []
            for h in self.testCandidates:
                for t in self.testCandidates[h]:
                    dataset.append( (self.testCandidates[h][t],self.isEvent(h,t), self.eventType(h,t) ) )
                    
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
            print("### {} {}".format(testMode,i+1))
            print("#############")
            self._selectDataset()
            self.testA = []
            self.trainA = []
            self.testB = []
            self.trainB = []
            self.testC =[]
            self.trainC = []
        
            #first train category classifier
            print("### TRAINING STEP 1: Training category classifier (Naive Bayes with word features) ###")
            for candidate, event, label in self.testData:
                featuresA = self.featureSelector.getFeatures(candidate, ['wordFeatures'])
                self.testA.append((featuresA, label))         
            
            for candidate, event, label in self.trainData:
                featuresA = self.featureSelector.getFeatures(candidate, ['wordFeatures'])
                self.trainA.append((featuresA, label))

            # MultinomialNB lijkt hier net zo goed als de nltk naive bayes classifier, maar is wel wat sneller
            self.classifierA = SklearnClassifier(MultinomialNB()).train(self.trainA)
            # sends the category classifier to the featureSelector
            self.featureSelector.addCategoryClassifier(self.classifierA)
                
            print("### TRAINING STEP 2: Training event/non-event classifier (Naive Bayes with category & other features) ###")
            # second step train the event/no event classifier
            for candidate, event, label in self.testData:
                featuresB = self.featureSelector.getFeatures(candidate, ['category','location','wordOverlapSimple','wordOverlapUser'])   
                self.featureKeys = featuresB.keys()
                self.testB.append((featuresB, event)) 
            
            for candidate, event, label in self.trainData:
                featuresB = self.featureSelector.getFeatures(candidate, ['category','location','wordOverlapSimple','wordOverlapUser'])
                self.featureKeys = featuresB.keys()
                self.trainB.append((featuresB, event))

            self.classifierB = nltk.NaiveBayesClassifier.train(self.trainB)

            
            print("### TRAINING STEP 3: Training final classifier (Final classifier) ###")
            for candidate, event, label in self.testData:
                featuresC = self.featureSelector.getFeatures(candidate, ['category','location','wordOverlapSimple','wordOverlapUser'])
                if self.classifierB.classify(featuresC) == 'event':
                    featuresC = self.featureSelector.getFeatures(candidate, ['wordFeatures'])
                    self.testC.append((featuresC, label))
                else:
                   self.testC.append((featuresC, self.categories[0]))      
            
            for candidate, event, label in self.trainData:
                featuresC = self.featureSelector.getFeatures(candidate, ['category','location','wordOverlapSimple','wordOverlapUser'])
                if self.classifierB.classify(featuresC) == 'event':
                    featuresC = self.featureSelector.getFeatures(candidate, ['wordFeatures'])
                    self.trainC.append((featuresC, label))
                else:
                   self.trainC.append((featuresC, self.categories[0]))  
            # MultinomialNB lijkt hier net zo goed als de nltk naive bayes classifier, maar is wel wat sneller
            self.classifierC = SklearnClassifier(MultinomialNB()).train(self.trainC)

            self.calculateStats(i)
            print("###########")
            
        self.printStats()

    def resultDictionary(self):
        return defaultdict(list)

    def calculateStats(self, i):
        '''Function to calculate all stats'''
        #self.table is for binary classifier
        #self.cm is for category classifier
        #self.mostInformativeBi is for binary
        #self.mostInformativeCat is for category
        #self.accBi  is accuracy for binary
        #self.accCat is accuracy for category
        # TODO meer stats voor cat?

        #calculate cm for this iteration
        ref = []
        tagged =[]
        for f, e in self.testA:
            ref.append(self.classifierA.classify(f))
            tagged.append(e)

        cm = nltk.ConfusionMatrix(ref, tagged)
        self.cm.append(cm)
       
        #calculate precision and recall for this iteration for each category
        refsets = defaultdict(set)
        testsets = defaultdict(set)
        

        for n, (feats, label) in enumerate(self.testC):
            refsets[label].add(n)
            observed = self.classifierC.classify(feats)
            testsets[observed].add(n)
        

        accuracy = nltk.classify.accuracy(self.classifierC,self.testC)
        self.acc += accuracy
        
        #for elke category precision and recall berekenen.
        for category in self.categories:
            if category in testsets:
                self.result[category]["p"].append(nltk.metrics.precision(refsets[category], testsets[category]))
                self.result[category]["r"].append(nltk.metrics.recall(refsets[category], testsets[category]))
                self.result[category]["f"].append(nltk.metrics.f_measure(refsets[category], testsets[category]))
            else:
                self.result[category]["p"].append(0)
                self.result[category]["r"].append(0)
                self.result[category]["f"].append(0)

        
    def eventType(self,geohash,timestamp):
        # return values {strings gebruiken?}
        eventTypes = {0:"geen_event", 1:"sport", 2:"entertainment", 3:"bijeenkomst", 4:"incident", 5:"anders"}
        return eventTypes[self.annotation[geohash][timestamp]]
        
    def isEvent(self,geohash,timestamp):
        # waarden groter/kleiner dan 0 zijn True, gelijk aan 0 is False
        if self.annotation[geohash][timestamp]:
            return 'event'
        else:
            return self.categories[0]

    def printStats(self):
        it = self.ITERATIONS
        print("\n### EVALUATION STEP 1: Confusion matrices for the category classifier:\n")
        for i in range(it):
            if self.realTest:
                testMode = "TEST"
            else:
                testMode = "DEVTEST"
            print("### {} {}".format(testMode,i+1))
            print("#############")
            print(self.cm[i])
        print("### EVALUATION STEP 2: Classification using features: {} | training set size: {} & test set size: {}\n".format(", ".join(self.featureKeys),len(self.trainC), len(self.testC)))
        for category in self.categories:
            table = []
            print("stats for", category)
            for i in range(it):
                table.append([str(i), round(self.result[category]["p"][i],2), round(self.result[category]["r"][i],2), round(self.result[category]["f"][i],2) ])
            print(tabulate.tabulate(table, headers=['#', 'P.', 'R', 'F']))
        print("Avg accuracy = {}".format(round(self.acc / (it) , 2)))
        #print("Avg baseline accuracy (everything is an event)= {}\n".format(round(self.baselineBi / (it) , 2)))

        #print(self.result)

# DEMO
if __name__ == "__main__":
    classifierCreator = ClassifierCreator()