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
import features
from modules import geohash
from collections import defaultdict, Counter
from math import log2,log
import datetime

class ClusterMerger:
    
    def __init__(self, clusters):
        # SETTINGS
        self.N_TWEETS = 2     # Min hoeveelheid tweets in candidate cluster
        self.UNIQUEUSERS = 2  # Min hoeveelheid tweets in candidate cluster
        self.THRESHOLD = 30   # Word overlap score om clusters samen te voegen
        self.MINUTES = 600    # Na hoeveel minuten kan een candidate cluster
                              # niet meer bij een ander candidate cluster horen?
        
        self.mergedClusters = [] # list om bij te houden welke clusters worden samengevoegd
        self.clusters = clusters
        self.idf = defaultdict(float)
        self._calculateIdf(self.clusters)
        # voeg clusters samen
        self._mergeClusters()
        self.eventCandidates = self._selectEventCandidates()
        self.createMarkers()
        
    # Bereken de idf-waarden gegeven (event) candidate clusters. Dit kan helaas niet zo heel
    # efficient in de huidige datastructuur.
    def _calculateIdf(self, clusters):
        print("Calculating idf for the candidate clusters...")
        n = 0
        for geoHash in clusters:
            for times in clusters[geoHash].keys():
                n += 1
                clusterwords = []
                for tweet in clusters[geoHash][times]:
                    for word in tweet["tokens"]:
                        clusterwords.append(word)
                for word in set(clusterwords):
                    self.idf[word] += 1
                    
        for word in self.idf:
            self.idf[word] = log2(n/self.idf[word])

    def _mergeClusters(self):
        print("Merging clusters...")
        
        clustersToAdd = []
        
        for geoHash in self.clusters:
            neighbors = geohash.neighbors(geoHash)
            # vergelijk ook met tijden in het eigen cluster
            neighbors.append(geoHash)
                        
            for neighbor in neighbors:
                if neighbor in self.clusters:
                    # er is een neigbor, dus alle timestamps vergelijken of er een neighbor is met dezelfde 
                    # timestamp plus of min 60 minuten
                    for timestamp in self.clusters[geoHash]:
                        for neighborTimestamp in self.clusters[neighbor]:
                            # geen cluster met zichzelf vergelijken wanneer de huidige neighbor de geoHash is
                            if neighbor == geoHash and timestamp == neighborTimestamp:
                                continue
                            if self._calculateTimeOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]) and \
                               self._calculateWordOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]):
                                clustersToAdd.append((geoHash, neighbor, timestamp, neighborTimestamp)) 
                                self.mergedClusters.append((geoHash,timestamp)) # for display
        
        #samenvoegen en verwijderen van samengevoegde clusters
        for geoHash, neighbor, timestamp, neighborTimestamp in clustersToAdd:
            self.clusters[geoHash][timestamp].extend(self.clusters[neighbor][neighborTimestamp])
            del self.clusters[neighbor][neighborTimestamp] # delete neighbor
        
    def _calculateTimeOverlap(self, cluster, neighborCluster):
        beginTime = cluster[0]['unixTime']
        endTime = cluster[-1]['unixTime']
        neighBeginTime = neighborCluster[0]['unixTime']
        neighEndTime = neighborCluster[-1]['unixTime']
        mins = self.MINUTES * 60
        
        # begin- of eindtijd van cluster ligt binnen neighborCluster of andersom
        if neighBeginTime - mins <= beginTime <= neighEndTime + mins or \
           neighBeginTime - mins <= endTime <= neighEndTime + mins or \
           beginTime - mins <= neighBeginTime <= endTime + mins or \
           beginTime - mins <= neighEndTime <= endTime + mins:
               return True

        return False

    def _calculateWordOverlap(self,clusterA, clusterB):      
        wordsClusterA = self._getImportantWords(20, clusterA)
        wordsClusterB = self._getImportantWords(20, clusterB)
        result = {}
        
        #intersect the two lists and adding the scores
        for wordA, scoreA in wordsClusterA:
            for wordB, scoreB in wordsClusterB:
                if wordA == wordB:
                    result[wordA] = scoreA + scoreB
                    #nog iets doen met hashtag, if hashtag score is * 2???
                    if wordA[0] == '#':
                        result[wordA] *= 2
                    if wordA[0] == '@':
                        result[wordA] *= 2
        if sum(result.values()) > self.THRESHOLD:
            return True
        else:
            return False
    
    def _getImportantWords(self, n, cluster):
        result = Counter()
        for tweet in cluster:
            for token in tweet["tokens"]:
                result[token] += self.idf[token] 
        return(result.most_common(n))
    
    def _eventCandidatesDic(self):
        return defaultdict(list)

    def _selectEventCandidates(self):
        print("Selecting event candidates...")
        
        nClusters = 0
        eventCandidates = defaultdict(self._eventCandidatesDic)
        for cluster in self.clusters:
            for times in self.clusters[cluster]:
                if len(self.clusters[cluster][times]) > self.N_TWEETS and features.uniqueUsers(self.clusters[cluster][times]) >= self.UNIQUEUSERS:
                    eventCandidates[cluster][times] = self.clusters[cluster][times]
                    nClusters += 1
       
        print("{} event candidates selected.".format(nClusters))
        return eventCandidates
            
    def getEventCandidates(self):
        return self.eventCandidates

    def createMarkers(self):
        print("Creating Google Maps markers...")
        
        js = open('vis/map/markers.js','w')
        js.write('var locations = [')

        # loop door clusters om te kijken wat event candidates zijn
        for hashes in self.eventCandidates:
            for times in self.eventCandidates[hashes]:   
                tweets = self.eventCandidates[hashes][times]
                
                writableCluster = ''
                
                i = 0
                avgLon = 0
                avgLat = 0
                              
                for tweet in tweets:
                    i = i + 1
                    
                    avgLon += float(tweet["lon"])
                    avgLat += float(tweet["lat"])
                    # backslashes voor multiline strings in Javascript
                    writableCluster += "{} {} {}<br/><br/>".format(tweet['localTime'], tweet['user'], tweet['text'].replace("'", "\\'"))
                # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
                # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
                # Oftewel, we doen even alsof de aarde plat is ;-)
                
                avgLon /= i
                avgLat /= i
                writableCluster += "Word overlap: {}, uniqueUsers: {} ".format(features.wordOverlapDisplay(tweets),features.uniqueUsers(tweets))
            # textfiles maken van alle afzonderlijke clusters en JS file maken voor Google maps
                #if (hashes, times) in self.mergedClusters:
                js.write("['{}', {}, {}],".format(writableCluster, avgLat,avgLon))
        js.write('];')
        js.close()
