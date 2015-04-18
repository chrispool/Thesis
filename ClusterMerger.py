#!/usr/bin/python3

"""
#############
ClusterMerger
#############
Voegt candidate clusters samen, gegeven een dictionary met clusters
gegenereerd door de ClusterCreator en idf-waarden gegenereerd door
de TweetPreprocessor. Clusters worden samengevoegd wanneer ze qua 
tijd, inhoud en onderwerp overlappen.
"""

import geohash
from collections import defaultdict, Counter

class ClusterMerger:
    
    def __init__(self, clusters, idf):
        # SETTINGS
        self.N_TWEETS = 2     # Min hoeveelheid tweets in candidate cluster
        self.UNIQUEUSERS = 2  # Min hoeveelheid tweets in candidate cluster
        self.THRESHOLD = 55   # Word overlap score om clusters samen te voegen
        self.MINUTES = 60     # Na hoeveel minuten kan een candidate cluster
                              # niet meer bij een ander candidate cluster horen?
        
        self.mergedClusters = [] # list om bij te houden welke clusters worden samengevoegd
        self.clusters = clusters
        self.idf = idf
        # TODO idf nog eens berekenen
        # TODO toptf-idf toevoegen voor selectie van "whitelist-users" voor een cluster
        # voeg clusters samen
        self.__mergeClusters()
        self.eventCandidates = self.__selectEventCandidates()
               
    def __mergeClusters(self):
        print("Merging candidate clusters...")
        for geoHash in self.clusters:
            neighbors = geohash.neighbors(geoHash)
            for neighbor in neighbors:
                if neighbor in self.clusters:
                    for timestamp in self.clusters[geoHash].keys():
                        # er is een neigbor, dus alle timestamps vergelijken of er een neighbor is met dezeflde 
                        # timestamp plus of min 60 minuten
                        for neighborTimestamp in self.clusters[neighbor].keys():
                            clustersToRemove = []
                            # Misschien hiervoor samen een betere oplossing verzinnen, 
                            # Nu hou ik een lijst met clusters die we moeten verwijderen bij omdat je 
                            # geen keys mag verwijderen in de loop
                            if abs(timestamp - neighborTimestamp) <= self.MINUTES * 60:
                                if self.__calculateOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]):
                                    self.clusters[geoHash][timestamp].extend(self.clusters[neighbor][neighborTimestamp])
                                    clustersToRemove.append((neighbor, neighborTimestamp))
                                    self.mergedClusters.append(geoHash+str(timestamp))
                        # verwijderen van samengevoegde clusters
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
            for token in tweet["tokens"]:
                result[token] += self.idf[token] 
        return(result.most_common(n))
    
    def __eventCandidatesDic(self):
        return defaultdict(list)

    def __selectEventCandidates(self):
        print("Selecting event candidates...")
        
        nClusters = 0
        eventCandidates = defaultdict(self.__eventCandidatesDic)
        for cluster in self.clusters:
            for times in self.clusters[cluster]:
                if len(self.clusters[cluster][times]) > self.N_TWEETS:
                    eventCandidates[cluster][times] = self.clusters[cluster][times]
                    nClusters += 1
                    
        # Nu hebben we dus de event candidates waarmee we feature selectie ed zouden
        # moeten uitvoeren!!!
                
                """userset = set()
                whiteList = False
                
                if len(self.clusters[cluster][times]) > self.N_TWEETS:
                    for tweet in self.clusters[cluster][times]:
                        username = tweet["user"].lower()
                        whiteListPrefix = ["112", "burgernet", "p2000"]
                        for prefix in whiteListPrefix:
                            if username.startswith(prefix):
                                whiteList = True
                                break
                        else:
                            userset.add(tweet["user"])
                              
                if len(userset) >= self.UNIQUEUSERS or whiteList:
                    eventCandidates[cluster][times] = self.clusters[cluster][times]
                    nClusters += 1
                """
        print("{} event candidates selected.".format(nClusters))
        return eventCandidates
            
    def getEventCandidates(self):
        return self.eventCandidates
