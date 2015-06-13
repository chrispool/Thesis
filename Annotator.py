#!/usr/bin/python3

"""
#############
Annotator
#############
Annotates dataset
"""
import sys,pickle,os,json
from collections import defaultdict


class Annotator:    
    
    def __init__(self, judge):
        self.dataSets = os.listdir('data/')
        self.judge = judge
        self.people = int(input("Are there two people going to annotate (2), or are you on your own (1)? "))
        if self.people == 1:
            print("\nYou entered 1. Good luck! :-)\n")
        else:
            print("\nYou entered 2. Don't forget to run AnnotationEvaluation.py when you are done! Good luck! :-)\n")
        self.annotation = {}
        self.candidates = {}
        self._loadDataSet()
        self._annotateCandidates()
        self._saveAnnotation()

    def _loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("\nSelect dataset: "))
        
        self.datasetName = self.dataSets[choice]

        jsonFile =  open("data/" + self.dataSets[choice] + "/eventCandidates.json")
        self.candidates = json.load(jsonFile)

    def _annotationDict(self):
        return defaultdict(list)

    def _annotateCandidates(self):
        self.annotatedEvents = defaultdict(self._annotationDict)
        #calculate n of clusters, dit moet makkelijker kunnen :)
        nClusters = 0
        for g in self.candidates:
            nClusters += len(self.candidates[g])
        
        nEvents = 0
        nCandidates = 0
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                nCandidates += 1
                print()
                print("---------{} van de {}-----------------".format(nCandidates, nClusters))
                print(self.formatTweets(self.candidates[geohash][timestamp]))
                print("--------------------------")
                print()
                eventTypes = {"geen event":0, "sport":1, "entertainment":2, "bijeenkomst":3, "incident":4, "anders":5}
                # sorteer event types voor weergave
                sortedEventTypes = sorted(eventTypes, key = eventTypes.get)
                eventString = "|"
                for eventType in sortedEventTypes:
                    eventString += " {}: {} |".format(eventType,eventTypes[eventType])
                eventString += " ==> "
                
                while True:
                    try:
                        choice = int(input('Event? ' + eventString))
                        if choice < 0 or choice > len(eventTypes)-1:
                            print("The number", choice, "does not represent an event.")
                        else:
                            self.annotatedEvents[geohash][timestamp] = choice
                            if choice: # 0 is geen event, dus False
                                nEvents += 1
                            break
                    except ValueError:
                        print("This is not a number, please try again.")
                    
        print("{} out of {} event candidates are events.".format(nEvents, nCandidates))

    def _saveAnnotation(self):
        print("Saving annotated data...")
        
        if self.people == 1:
            # only 1 person annotating: no need to run AnnotationEvaluation, annotation
            # and event candidates are automatically sanitized.
            filenameSEC = 'data/' + self.datasetName + '/sanitizedEventCandidates.json'
            with open(filenameSEC, 'w') as outfile:
                json.dump(self.candidates, outfile)
            
            filenameSAN = 'data/' + self.datasetName + '/sanitizedAnnotation.json'
            with open(filenameSAN, 'w') as outfile:
                json.dump(self.annotatedEvents, outfile)
                
        filenameA = 'data/' + self.datasetName + '/annotation_' + self.judge + '.json'
        with open(filenameA, 'w') as outfile:
            json.dump(self.annotatedEvents, outfile)

    def formatTweets(self, cluster):
        text = [tweet['user'] + ' -> ' + tweet['text'] for tweet in cluster]
        text.append((" "))
        
        return '\n'.join(text)

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("use: Annotator.py Name-judge")
    else:
        a = Annotator(sys.argv[1])
