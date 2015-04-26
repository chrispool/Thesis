#!/usr/bin/python3

"""
#############
eventCandidates
#############
Generates eventCandidates and exports dataset to folder
"""
import sys,pickle,os,json,time
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
        self.saveDateset() 
        
    def saveDateset(self):
        print("Saving event candidates...")
        #create dataset folder
        if not os.path.isdir('data/' + sys.argv[2]):
             os.makedirs('data/' + sys.argv[2])
        
        filenameEC = 'data/' + sys.argv[2] + '/eventCandidates.json'

        with open(filenameEC, 'w') as outfile:
            json.dump(self.eventCandidates, outfile)

if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("use: eventCandidates.py tweetfile datasetname")
    else:
        start = time.time()
        ec = EventCandidates(sys.argv[1])
        print("Creating event candidates took", time.time() - start, "seconds.")
        