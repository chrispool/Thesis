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
from collections import defaultdict, Counter
import msgpack

class ClusterMerger:
    
    def __init__(self, tweetFile):
        # maak of leeg de map met clusters
        self.__emptyClusterFolder()
        self.THRESHOLD = 55 #wordoverlap score om clusters samen te voegen
        self.mergedClusters = [] #list om bij te houden welke clusters worden samengevoegd
        
        self.creator = ClusterCreator(tweetFile)
        self.clusters = self.creator.getClusters()
        self.idf = self.creator.getIdf()
        # voeg clusters samen
        self.__mergeClusters()
        self.eventCandidates = self.__selectEventCandidates()
               
    def __mergeClusters(self):
        for geoHash in self.clusters:
            neighbors = geohash.neighbors(geoHash)
            for neighbor in neighbors:
                if neighbor in self.clusters:
                    for timestamp in self.clusters[geoHash].keys():
                        # er is een neigbor, dus alle timestamps vergelijken of er een neighbor is met dezeflde 
                        # timetsamp plus of min 60 minuten
                        for neighborTimestamp in self.clusters[neighbor].keys():
                            clustersToRemove = []
                            # Misschien hiervoor samen een betere oplossing verzinnen, 
                            # Nu hou ik een lijst met clusters die we moeten verwijderen bij omdat je 
                            # geen keys mag verwijderen in de loop
                            if abs(timestamp - neighborTimestamp) <= self.creator.MINUTES * 60:
                                if self.__calculateOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]):
                                    self.clusters[geoHash][timestamp].extend(self.clusters[neighbor][neighborTimestamp])
                                    clustersToRemove.append((neighbor, neighborTimestamp))
                                    self.mergedClusters.append(geoHash+str(timestamp))
                        #verwijderen van samengevoegde clusters
                        for c, t in clustersToRemove:
                            if t in self.clusters[c].keys():
                                del self.clusters[c][t]

                                 
    def __calculateOverlap(self,clusterA, clusterB):      
        wordsClusterA = self.__getImportantWords(10, clusterA)
        wordsClusterB = self.__getImportantWords(10, clusterB)
        result = {}
        
        #intersect the two lists and adding the scores
        for wordA, scoreA in wordsClusterA:
            for wordB, scoreB in wordsClusterB:
                if wordA == wordB:
                    result[wordA] = scoreA + scoreB

        if sum(result.values()) > self.THRESHOLD:
            return True
        else:
            return False
    

    def __getImportantWords(self, n, cluster):
        result = Counter()
        for tweet in cluster:
            if "tokens" in tweet:
                for token in tweet["tokens"]:
                    result[token] += self.idf[token] 
        return(result.most_common(n))
    
    def __eventCandidatesDic(self):
        return defaultdict(list)

    def __selectEventCandidates(self):
        print("Select clusters")
        nClusters = 0
        eventCandidates = defaultdict(self.__eventCandidatesDic)
        for cluster in self.clusters:
            for times in self.clusters[cluster]:    
                
                userlist = []
                # cluster bevat meer dan N_TWEETS
                if len(self.clusters[cluster][times]) > self.creator.N_TWEETS:
                    for tweet in self.clusters[cluster][times]:
                        if 'user' in tweet:
                            userlist.append(tweet["user"])                  
                              
                if len(set(userlist)) >= self.creator.UNIQUEUSERS:
                    eventCandidates[cluster][times] = self.clusters[cluster][times]
                    nClusters += 1
        print("{} clusters selected.".format(nClusters)) 
        return eventCandidates
        
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
