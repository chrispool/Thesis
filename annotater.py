#!/usr/bin/python3

"""
#############
annotater
#############
Annotates dataset
"""
import sys,pickle,os,json
from collections import defaultdict
import features

class Annotater:    
    
    def __init__(self, judge):
        self.dataSets = os.listdir('data/')
        self.judge = judge
        self.annotation = {}
        self.candidates = {}
        self.__loadDataSet()
        self.annotateCandidates()
        self.saveAnnotation()

        
    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        self.datasetName = self.dataSets[choice]

        jsonFile =  open("data/" + self.dataSets[choice] + "/eventCandidates.json")
        self.candidates = json.load(jsonFile)


    def __annotationDict(self):
        return defaultdict(list)

    def annotateCandidates(self):
        self.annotatedEvents = defaultdict(self.__annotationDict)
        nEvents = 0
        nCandidates = 0
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                nCandidates += 1
                print()
                print("--------------------------")
                print(self.formatTweets(self.candidates[geohash][timestamp]))
                print("--------------------------")
                print()
                eventTypes = {"geen event":0, "sport":1, "politiek":2, "bijeenkomst":3, "ongeval":4, "concert":5, "anders":6}
                # sorteer event types voor weergave
                sortedEventTypes = sorted(eventTypes, key = eventTypes.get)
                eventString = "|"
                for eventType in sortedEventTypes:
                    eventString += " {}: {} |".format(eventType,eventTypes[eventType])
                eventString += " "
                
                while True:
                    try:
                        choice = int(input('Event? ' + eventString))
                        if choice < 0 or choice > len(eventTypes)-1:
                            print("Het nummer", choice, "representeert geen event.")
                        else:
                            self.annotatedEvents[geohash][timestamp] = choice
                            if choice: # 0 is geen event, dus False
                                nEvents += 1
                            break
                    except ValueError:
                        print("Dit is geen nummer, probeer opnieuw.")
                    
                if nCandidates == 1000:
                    print("Total of {} are events of the {} candidates".format(nEvents, nCandidates))
                    return
     
    def saveAnnotation(self):
        print("Geannoteerde data opslaan...")
 
        filenameA = 'data/' + self.datasetName + '/annotation_' + self.judge + '.json'
        with open(filenameA, 'w') as outfile:
            json.dump(self.annotatedEvents, outfile)

    def formatTweets(self, cluster):
        text = [tweet['user'] + ' -> ' + tweet['text'] for tweet in cluster]
        return '\n'.join(text)

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("use: annotation.py Name-judge")
    else:
        a = Annotater(sys.argv[1])
