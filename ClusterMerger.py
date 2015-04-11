#!/usr/bin/python3

"""
#############
ClusterMerger
#############
Voegt event candidate clusters samen, gegeven een .txt-bestand met tweets 
in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

Clusters worden samengevoegd wanneer ze qua tijd, inhoud en onderwerp 
overlappen.
"""

import os, sys, time, geohash
from ClusterCreator import ClusterCreator
from collections import defaultdict

class ClusterMerger:
    
    def __init__(self, tweetFile):
        creator = ClusterCreator(tweetFile)
        self.clusters = creator.getClusters()
        self.idf = creator.getIdf()
        # voeg clusters samen
        self.__mergeClusters()
        # maak of leeg de map met clusters
        self.__emptyClusterFolder()
        
    def __mergeClusters(self):
        for geoHash in self.clusters:
            neighbors = geohash.neighbors(geoHash)
            for neighbor in neighbors:
                if neighbor in self.clusters:
                    # TODO: kijk of de clusters qua tijd/inhoud overlappen
                    pass
    
    def __emptyClusterFolder(self):
        if not os.path.isdir("clusters"): 
            # clustermap bestaat nog niet
            os.makedirs("clusters")
            print("Created a new cluster folder.")
        else:
            # clustermap bestaat, haal oude clusters weg
            filelist = [f for f in os.listdir("clusters/") if f.endswith(".txt")]
            for f in filelist:
                os.remove('clusters/' + f)
            print("Emptied the cluster folder.")
            
if __name__ == "__main__":
    merger = ClusterMerger(sys.argv[1])
