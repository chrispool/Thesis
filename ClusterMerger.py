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
        self.MINUTES = 60     # Na hoeveel minuten kan een candidate cluster
                              # niet meer bij een ander candidate cluster horen?
        
        self.mergedClusters = [] # list om bij te houden welke clusters worden samengevoegd
        self.clusters = clusters
        self.idf = defaultdict(float)
        self.__calculateIdf(self.clusters)
        # voeg clusters samen
        self.__mergeClusters()

        self.eventCandidates = self.__selectEventCandidates()
        self.createMarkers()
        
        
    # Bereken de idf-waarden gegeven (event) candidate clusters. Dit kan helaas niet zo heel
    # efficient in de huidige datastructuur.
    def __calculateIdf(self, clusters):
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
    
    # bereken de top tf-idf woorden voor een cluster. 
    # TODO Dit kan misschien nog iets mooier
    # TODO Selectie van "whitelist-users" voor een cluster
    def __topTfIdf(self, tweetCluster, n = 5):
        tfIdfDict = defaultdict(float)
        # bepaal de tf-waarden
        for tweet in tweetCluster:
            for word in tweet["tokens"]:
                tfIdfDict[word] += 1
        # vermenigvuldig nu tf met idf (dit gedeelte kan ook weggelaten
        # worden om te testen met alleen tf!)
        for word in tfIdfDict:
            tfIdfDict[word] *= self.idf[word]
        # en geef een set van de top n woorden terug
        sort = set(sorted(tfIdfDict.items(), key = itemgetter(1), reverse = True)[:n])
        topTfIdf = set()
        for word,tfIdf in sort:
            topTfIdf.add(word)
        
        return topTfIdf

    def __mergeClusters(self):
        for geoHash in self.clusters:
            neighbors = geohash.neighbors(geoHash)
            for neighbor in neighbors:
                if neighbor in self.clusters:
                    for timestamp in self.clusters[geoHash].keys():
                        # er is een neigbor, dus alle timestamps vergelijken of er een neighbor is met dezeflde 
                        # timetsamp plus of min 60 minuten
                        for neighborTimestamp in self.clusters[neighbor].keys():
                            clustersToAdd = []
                            # Misschien hiervoor samen een betere oplossing verzinnen, 
                            # Nu hou ik een lijst met clusters die we moeten verwijderen bij omdat je 
                            # geen keys mag verwijderen in de loop
                            if self.__calculateTimeOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]) == True:
                                if self.__calculateOverlap(self.clusters[geoHash][timestamp], self.clusters[neighbor][neighborTimestamp]):
                                    # is de key al in de lijst te verwijderen clusters dan niet meer gebruiken   
                                    clustersToAdd.append((neighbor, neighborTimestamp)) 
                                    self.mergedClusters.append((geoHash,timestamp)) # for display

                        #samenvoegen en verwijderen van samengevoegde clusters
                        for c, t in clustersToAdd:
                            self.clusters[geoHash][timestamp].extend(self.clusters[c][t])
                            del self.clusters[c][t] #delete neighbour

                                 
    def __calculateTimeOverlap(self, cluster, neighbourCluster):
        clusterT = sorted([ row['unixTime'] for row in cluster ])
        neighbourClusterT = sorted([ row['unixTime'] for row in neighbourCluster ])
        for t in neighbourClusterT: 
            if clusterT[0] - (self.MINUTES * 60) <= t <= clusterT[-1] - (self.MINUTES * 60):
                return True

        return False

        


    def __calculateOverlap(self,clusterA, clusterB):      
        wordsClusterA = self.__getImportantWords(20, clusterA)
        wordsClusterB = self.__getImportantWords(20, clusterB)
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

