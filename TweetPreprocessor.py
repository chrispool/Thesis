#!/usr/bin/python3

"""
#################
TWEETPREPROCESSOR
#################
Maakt op dit moment een lijst van tweet dictionaries, gegeven een
.txt-bestand met tweets in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

Een tweet-dictionary bevat de volgende (keys) gegevens voor elke tweet:
* text      : de tekst
* tokens    : lijst van woorden (grof getokeniseerde tekst)
* lon       : de lengtegraad
* lat       : de breedtegraad
* user      : de gebruikersnaam
* unixTime  : lokale tijd, geconverteerd naar Unix Time
* localTime : lokale tijd, zoals weergegeven in de tweet
* geoHash   : de geoHash waarin deze tweet is gepost

Hiernaast wordt ook een dictionary met idf-waarden aangemaakt. Zowel
het idf-dictionary en de tweet dictionaries worden opgeslagen in een
bin-bestand, waarbij ook de bestandsnaam van het bestand met tweets 
wordt opgeslagen (in het idf-dictionary). Wordt de TweetPreprocessor 
gedraaid met die bestandsnaam, dan worden de opgeslagen dictionaries
gebruikt, anders worden ze opnieuw gegenereerd.
"""

import sys, re, math, geohash, time, datetime, msgpack
from collections import defaultdict

class TweetPreprocessor:
    
    def __init__(self, tweetFile):
        # SETTINGS
        self.HASH_ACCURACY = 7 # precisie van geoHash
        
        # regex pattern voor simpele tokenisatie: alles behalve letters, 
        # cijfers en underscores wordt vervangen door een spatie
        self.pat = re.compile('[\W]+')
        # Nederlandse stopwoorden (NLTK stopwoorden plus een lijst op internet)
        self.stoplist = \
        ["aan", "afd", "als", "bij", "ik", "mij", "we", "wij", "jij", "je", "jou", "ons", "jullie", "dat",
         "u", "hij", "zij", "hem", "haar", "de", "den", "der", "des", "deze", "die", "dit", "dl", "door",
         "dr", "ed", "een", "en", "enige", "enkele", "enz", "et", "etc", "het", "hierin", "hoe", "hun",
         "in", "inzake", "is", "met", "na", "naar", "nabij", "niet", "no", "nu", "of", "om", "onder",
         "onze", "ook", "oorspr", "op", "over", "pas", "pres", "prof", "publ", "sl", "st", "te", "tegen",
         "ten", "ter", "tot", "uit", "uitg", "vakgr", "van", "vanaf", "vert", "vol", "voor", "voortgez",
         "wat", "wie", "zijn", "waar", "wanneer", "was", "had", "er", "maar", "dan", "zou", "mijn", "men",
         "zo", "ze", "zich", "heb", "daar", "heeft", "hebben", "want", "nog", "zal", "me", "ge", "gij",
         "geen", "iets", "worden", "toch", "al", "waren", "veel", "meer", "doen", "toen", "moet", "ben",
         "zonder", "kan", "dus", "alles", "ja", "eens", "hier", "werd", "altijd", "doch", "wordt", "wezen",
         "kunnen", "zelf", "reeds", "wil", "kon", "niets", "uw", "iemand", "geweest", "andere"]
        
        self.tweetDicts, self.idf = self.__createTweetDicts(tweetFile)
        
    # Laad een bestand met msgpack
    def __load_file(self, f):
        try:
            with open(f, "rb") as f:
                d = msgpack.load(f, encoding='utf-8')
                return d
        except:
            return False    

    def __tokenize(self, text):
        tokens = text.split()
        # filter links
        for word in tokens[:]:
            if word.startswith("http:"):
                tokens.remove(word)
        filterLinkText = ' '.join(tokens)
        # vervang alles behalve letters/cijfers door een spatie
        tokens = self.pat.sub(' ', filterLinkText).lower().split()
        # filter stopwoorden, cijfers en losse karakters
        for word in tokens[:]:
            if word in self.stoplist or word.isdigit() or len(word) < 2:
                tokens.remove(word)
        # filter dubbele woorden
        return list(set(tokens))
        
    # Maak de lijst van tweet dictionaries en bereken meteen alle idf-waarden
    def __createTweetDicts(self, tweetFile):
        
        # zijn het idf-dictionary en de tweet dictionaries al eerder gemaakt?
        idf = self.__load_file("idf.bin")
        tweetDicts = self.__load_file("tweetdicts.bin")
        
        if idf and "%FILENAME%:" + tweetFile in idf and tweetDicts:
            print("Successfully loaded the earlier generated binary files for ", tweetFile, "!", sep = "")
            return tweetDicts, idf
        
        print("Creating new tweet dictionaries and an idf dictionary for ", tweetFile, ".", sep = "")
        idf = defaultdict(float)
        tweetDicts = []

        with open(tweetFile) as f:
            for line in f:
                tweetElements = line.strip().split('\t')
                text = tweetElements[0]
                tokens = self.__tokenize(text)
                coords = tweetElements[1].split()
                lat, lon = float(coords[1]), float(coords[0])
                # maak een geoHash met precisie HASH_ACCURACY
                geoHash = geohash.encode(lat, lon, self.HASH_ACCURACY)
                # converteer de tijd van de tweet naar Unix Time
                tweetTime = ' '.join(tweetElements[3].split()[:2])
                unixTime = int(time.mktime(datetime.datetime.strptime(tweetTime, "%Y-%m-%d %H:%M:%S").timetuple()))
                # zet alle waarden in een tweet dictionary
                tweetDicts.append({"text"      : text,
                                   "tokens"    : tokens,
                                   "lon"       : lon,
                                   "lat"       : lat,
                                   "user"      : tweetElements[2],
                                   "unixTime"  : unixTime,
                                   "localTime" : tweetTime,
                                   "geoHash"   : geoHash})
                for word in tokens:
                    idf[word] += 1

        # bereken idf-score voor ieder woord
        n = len(idf)
        for word in idf:
            idf[word] = math.log10(n / idf[word])

        print("Done! Dumping dictionaries to disk...")
        with open('idf.bin', 'wb') as f:
            idf["%FILENAME%:" + tweetFile] = 1
            msgpack.dump(idf, f)
        print("* idf.bin is ready...")
        
        with open('tweetdicts.bin', 'wb') as f:
            msgpack.dump(tweetDicts, f)
        print("* tweetdicts.bin is ready...")
            
        return tweetDicts, idf
    
    def getTweetDicts(self):
        return self.tweetDicts
        
    def getIdf(self):
        return self.idf
    
# DEMO
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./TweetPreprocessor.py tweetFile")
        sys.exit()
    fetcher = TweetPreprocessor(sys.argv[1])
    tweetDicts = fetcher.getTweetDicts()
    idf = fetcher.getIdf()
    for tweet in tweetDicts[:5]:
        print(tweet)
        for word in tweet["tokens"]:
            print(word, idf[word])