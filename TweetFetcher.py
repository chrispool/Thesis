#!/usr/bin/python3

"""
############
TWEETFETCHER
############
Maakt op dit moment een lijst van tweet dictionaries, gegeven een
.txt-bestand met tweets in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

Een tweet-dictionary bevat de volgende (keys) gegevens voor elke tweet:
* text    : de tekst
* tokens  : lijst van woorden (grof getokeniseerde tekst)
* lon     : de lengtegraad
* lat     : de breedtegraad
* user    : de gebruikersnaam
* time    : de tijd, geconverteerd naar Unix Time
* geoHash : de geoHash waarin deze tweet is gepost

TODO: Misschien een optie toevoegen waarmee de TweetFetcher 
automatisch voor een bepaald tijdsinterval tweets van Karora haalt?
Alles in een database zetten is natuurlijk wel mooi, maar ik heb er
verder nog niet echt tijd voor gehad.
"""

import sys, re, math, geohash, time, datetime
from collections import defaultdict

class TweetFetcher:
    
    def __init__(self, tweetFile):
        # SETTINGS
        self.HASH_ACCURACY = 6 # precisie van geoHash
        
        self.tweetDicts, self.idf = self.__createTweetDicts(tweetFile)
        
    # Maak de lijst van tweet dictionaries en bereken meteen alle idf-waarden
    def __createTweetDicts(self, tweetFile):
        
        idf = defaultdict(float)
        tweetDicts = []
        # regex pattern voor simpele tokenisatie: alles behalve letters, 
        # cijfers en underscores wordt vervangen door een spatie
        pat = re.compile('[\W]+')
        
        with open(tweetFile) as f:
            for line in f:
                tweetElements = line.strip().split('\t')
                text = tweetElements[0]
                tokens = pat.sub(' ', text).lower().split()
                coords = tweetElements[1].split()
                lat, lon = float(coords[1]), float(coords[0])
                # maak een geoHash met precisie HASH_ACCURACY
                geoHash = geohash.encode(lat, lon, self.HASH_ACCURACY)
                # converteer de tijd van de tweet naar unix time
                tweetTime = ' '.join(tweetElements[3].split()[:2])
                unixTime = int(time.mktime(datetime.datetime.strptime(tweetTime, "%Y-%m-%d %H:%M:%S").timetuple()))
                # zet alle waarden in een tweet dictionary
                tweetDicts.append({"text"    : text,
                                   "tokens" :  tokens,
                                   "lon"     : lon,
                                   "lat"     : lat,
                                   "user"    : tweetElements[2],
                                   "time"    : unixTime,
                                   "geoHash" : geoHash})
                for word in tokens:
                    idf[word] += 1
        
        # bereken idf-score voor ieder woord
        n = len(idf)
        for word in idf:
            idf[word] = math.log10(n / idf[word])
            
        return tweetDicts, idf
    
    def getTweetDicts(self):
        return self.tweetDicts
        
    def getIdf(self):
        return self.idf
    
# DEMO
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./TweetFetcher.py tweetFile")
        sys.exit()
    fetcher = TweetFetcher(sys.argv[1])
    tweetDicts = fetcher.getTweetDicts()
    idf = fetcher.getIdf()
    for tweet in tweetDicts[:5]:
        print(tweet)
        for word in tweet["tokens"]:
            print(word, idf[word])
