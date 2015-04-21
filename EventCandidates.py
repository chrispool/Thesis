#!/usr/bin/python3

"""
#############
eventCandidates
#############
Generates eventCandidates and annotates and exports dataset to folder
"""
import sys,pickle,os,json
from TweetPreprocessor import TweetPreprocessor
from ClusterCreator import ClusterCreator
from ClusterMerger import ClusterMerger
from collections import defaultdict

class EventCandidates:    
    def __init__(self, tweetFile):
        # preprocess tweets in tweetFile
        preprocessor = TweetPreprocessor(tweetFile)
        tweetDicts = preprocessor.getTweetDicts()
        # maak candidate clusters
        creator = ClusterCreator(tweetDicts)
        clusters = creator.getClusters()
        # voeg candidate clusters samen tot event candidates
        merger = ClusterMerger(clusters)
        self.eventCandidates = merger.getEventCandidates()

        self.annotatedEvents = defaultdict(self.__annotationDict)
        self.annotateCandidates()
        self.saveDateset()
        
    def __annotationDict(self):
        return defaultdict(list)

    def annotateCandidates(self):
        nEvents = 0
        nCandidates = 0
        for geohash in self.eventCandidates:
            for timestamp in self.eventCandidates[geohash]:
                nCandidates += 1
                print()
                print("--------------------------")
                print(self.formatTweets(self.eventCandidates[geohash][timestamp]))
                print("--------------------------")
                print()
                eventTypes = {"geen event":0, "sport":1, "politiek":2, "bijeenkomst":3, "ongeval":4, "concert":5}
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
                    except:
                        print("\nGij zult de annotatie afmaken!")
                
                if nCandidates == 100:
                    print("Total of {} are events of the {} candidates".format(nEvents, nCandidates))
                    return
     
    def saveDateset(self):
        print("Save dataset.")
        #create dataset folder
        if not os.path.isdir('data/' + sys.argv[2]):
             os.makedirs('data/' + sys.argv[2])
        
        filenameEC = 'data/' + sys.argv[2] + '/eventCandidates.json'
        filenameA = 'data/' + sys.argv[2] + '/annotation.json'

        with open(filenameEC, 'w') as outfile:
            json.dump(self.eventCandidates, outfile)
        with open(filenameA, 'w') as outfile:
            json.dump(self.annotatedEvents, outfile)

    def formatTweets(self, cluster):
        text = [tweet['user'] + ' -> ' + tweet['text'] for tweet in cluster]
        return '\n'.join(text)

if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("use: eventCandidates.py tweetfile datasetname")
    else:
        ec = EventCandidates(sys.argv[1])
