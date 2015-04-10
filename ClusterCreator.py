#!/usr/bin/python3

"""
##############
ClusterCreator
##############
Maakt event candidate clusters, gegeven een .txt-bestand met tweets 
in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

Clusters bestaan uit tweets die binnen een bepaalde geoHash en tijd
zijn gepost. Daarnaast wordt voor nieuwe tweets gekeken of ze minstens 
1 van de n woorden met de hoogste tf-idf score van het cluster tot nu 
toe bevatten.
"""

import os, sys, time
from TweetPreprocessor import TweetPreprocessor
from collections import defaultdict
from operator import itemgetter

class ClusterCreator:
    
    def __init__(self, tweetFile):
        # SETTINGS
        self.MINUTES = 60     # Na hoeveel minuten kan een tweet niet meer
                              # bij een event horen?
        self.N_TWEETS = 3     # Min hoeveelheid tweets in candidate cluster
        self.UNIQUEUSERS = 3  # Unieke gebruikers in een cluster
        self.UNIQUECOORDS = 3 # Unieke coordinaten in een cluster
        
        fetcher = TweetPreprocessor(tweetFile)
        # voor de keys van de tweet dictionaries, zie TweetPreprocessor.py
        self.tweetDicts = fetcher.getTweetDicts()
        self.idf = fetcher.getIdf()
        # maak of leeg de map met clusters
        self.__emptyClusterFolder()
        self.clusters = defaultdict(self.__timeTweetDict)
        self.topTfIdf = defaultdict(self.__timeTweetDict)
        self.__createClusters()
        self.__selectEventCandidates()
        
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
            
    def __timeTweetDict(self):
        return defaultdict(list)
    
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
            
    def __createClusters(self):
        print("Creating tweet clusters...")
    
        for tweet in self.tweetDicts:
            geoHash = tweet["geoHash"]
            tweetTime = tweet["unixTime"]

            if geoHash in self.clusters:
                for times in self.clusters[geoHash].keys():
                    if times <= tweetTime <= times + self.MINUTES * 60:
                        tweetSet = set(tweet["tokens"])
                        # komen de woorden van de tweet en de belangrijkste n woorden
                        # van het cluster overeen?
                        if len(tweetSet & self.topTfIdf[geoHash][times]) > 0:
                            self.clusters[geoHash][times].append(tweet)
                            # bereken topTfIdf voor de nieuwe cluster
                            self.topTfIdf[geoHash][tweetTime] = self.__topTfIdf(self.clusters[geoHash][times])
                            # zet de tijd vooruit naar de tijd van de nieuwe tweet
                            # om het event in leven te houden
                            self.clusters[geoHash][tweetTime] = self.clusters[geoHash][times]
                            # verwijder de cluster op de oude tijd
                            if tweetTime != times:
                                del self.clusters[geoHash][times]
                                del self.topTfIdf[geoHash][times]
                            break
                else:
                    # Alle tijden gehad waarin deze tweet had kunnen passen, maar deze 
                    # tweet past nergens! Nieuwe cluster maken.
                    self.clusters[geoHash][tweetTime].append(tweet)
                    self.topTfIdf[geoHash][tweetTime] = self.__topTfIdf(self.clusters[geoHash][tweetTime])
            else:
                # geoHash bestaat nog niet! Voeg tijd en tweet toe aan nieuwe geoHash.
                self.clusters[geoHash][tweetTime].append(tweet)
                self.topTfIdf[geoHash][tweetTime] = self.__topTfIdf(self.clusters[geoHash][tweetTime])
        
    def __selectEventCandidates(self):
        print("Selecting event candidates...")
        
        js = open('markers.js','w')
        js.write('var locations = [')
        
        # loop door clusters om te kijken wat event candidates zijn
        for hashes in self.clusters:
            for times in self.clusters[hashes]:
                # tweets is de lijst van tweets in het cluster
                tweets = self.clusters[hashes][times]
                
                userlist = []
                geolist = []

                # cluster bevat meer dan N_TWEETS
                if len(tweets) > self.N_TWEETS:
                    for tweet in tweets:
                        if not tweet["user"] in userlist:       # toevoegen aan lijst met unieke users van dit cluster
                            userlist.append(tweet["user"])
                        location = (tweet["lat"], tweet["lon"])
                        if not location in geolist:             # toevoegen aan lijst met unieke locaties van dit cluster
                            geolist.append(location)

                writableCluster = ""
                i = 0
                avgLon = 0
                avgLat = 0
                # cluster pas opslaan wanneer er meerdere unieke gebruikers en locaties in staan
                if len(userlist) >= self.UNIQUEUSERS and len(geolist) >= self.UNIQUECOORDS:
                    with open('clusters/' + hashes + '-' + str(times) + '.txt','w') as f:
                        js.write("['")
                        writableCluster += "{}<br/><br/>".format(str(self.topTfIdf[hashes][times]).replace("'", "\\'"))
                        for tweet in tweets:
                            i = i + 1
                            avgLon += tweet["lon"]
                            avgLat += tweet["lat"]
                            # backslashes voor multiline strings in Javascript
                            writableCluster += "{} {} {}<br/><br/>\\\n".format(tweet["localTime"], 
                                                tweet["user"], tweet["text"].replace("'", "\\'"))
                        # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
                        # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
                        # Oftewel, we doen even alsof de aarde plat is ;-)
                        avgLon /= i
                        avgLat /= i
                        # textfiles maken van alle afzonderlijke clusters en JS file maken voor Google maps
                        f.write(writableCluster + "{} {}".format(avgLat,avgLon))
                        js.write(writableCluster[:-2] + "{} {}', {}, {}],\n".format(avgLat,avgLon,avgLat,avgLon))
        js.write('];')
        js.close()

# DEMO
if __name__ == "__main__":
    start = time.time() 
    if len(sys.argv) != 2:
        print("./ClusterCreator.py tweetFile")
        sys.exit()
    creator = ClusterCreator(sys.argv[1])
    runTime = time.time() - start
    print("Finding clusters and selecting event candidates took", runTime, "seconds.")