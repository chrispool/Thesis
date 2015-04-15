#!/usr/bin/python3

"""
#############
eventCandidates
#############
Generates eventCandidates and annotates and exports dataset to folder
"""
import sys,pickle,os,json
from ClusterMerger import ClusterMerger
from collections import defaultdict

class EventCandidates:    
    def __init__(self, tweetFile):   
        self.merger = ClusterMerger(tweetFile)
        self.idf = self.merger.creator.getIdf()
        self.annotatedEvents = defaultdict(self.__annotationDict)
        self.annotateCandidates()
        self.saveDateset()
        
    def __annotationDict(self):
        return defaultdict(list)

    def annotateCandidates(self):
        nEvents = 0
        nCandidates = 0
        for geohash in self.merger.eventCandidates:
            for timestamp in self.merger.eventCandidates[geohash]:
                nCandidates += 1
                print()
                print("--------------------------")
                print(self.formatTweets(self.merger.eventCandidates[geohash][timestamp]))
                print("--------------------------")
                print()
                #choice = input('Cluster? j/n ')
                choice = 'j'
                if choice == 'j':
                    self.annotatedEvents[geohash][timestamp] = True
                    nEvents += 1
                else:
                    self.annotatedEvents[geohash][timestamp] = False

        print("Total of {} are events of the {} candidates".format(nEvents, nCandidates))
     
    def saveDateset(self):
        print("Save dataset.")
        #create dataset folder
        if not os.path.isdir('data/' + sys.argv[2]):
             os.makedirs('data/' + sys.argv[2])
        
        filenameEC = 'data/' + sys.argv[2] + '/eventCandidates.json'
        filenameA = 'data/' + sys.argv[2] + '/annotation.json'

        with open(filenameEC, 'w') as outfile:
            json.dump(self.merger.eventCandidates, outfile)
        with open(filenameA, 'w') as outfile:
            json.dump(self.annotatedEvents, outfile)
                


    
 
    
    def formatTweets(self, cluster):
        text = [tweet['text'] for tweet in cluster]
        return ('\n'.join(text))

               
    
            
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("use: eventCandidates.py tweetfile datasetname")
    else:
        ec = EventCandidates(sys.argv[1])
