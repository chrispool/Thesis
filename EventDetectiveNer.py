#!/usr/bin/env python3
from nltk.tag.stanford import NERTagger 
import nltk
import subprocess
from EventDetective import EventDetective
from operator import itemgetter
from collections import defaultdict, Counter

class EventDetectiveNer(EventDetective):
    
    def loadClassifier(self):
        classifier = "ner/classifiers/" + "tweets.ser.gz"
        jar = "ner/stanford-ner-3.4.jar"
        self.tagger = NERTagger(classifier, jar)

    def tagText(self, candidate):
        result = defaultdict(list)
        text = " ".join([tweet['text'] for tweet in candidate]) #make one long text     
        for line in self.tagger.tag(nltk.word_tokenize(text)):
            for word, tag in line:
                result[tag].append(word)
        return result
            
    def generateMarkers(self):
        print("Creating Google Maps markers & add WIKI links...")
        
        js = open('vis/map/js/markers.js','w')
        js.write('var locations = [')

        
        for tweets,label in self.events:
            writableCluster = ''
            gh = []
            i = 0
            avgLon = 0
            avgLat = 0
            #tweets = sorted(tweets, key=itemgetter('unixTime'));
                              
            for tweet in tweets:
                i = i + 1
                gh.append(tweet['geoHash'])
                avgLon += float(tweet["lon"])
                avgLat += float(tweet["lat"])
                # backslashes voor multiline strings in Javascript
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text']).replace("'", "\\'")
            # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
            # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
            # Oftewel, we doen even alsof de aarde plat is ;-)
            avgLon /= i
            avgLat /= i
            nertags = self.tagText(tweets)
            for key in nertags:
                if key != 'O':
                    writableCluster += "</br> {} {}".format(key, " ,".join(list(set(nertags[key]))).replace("'", "\\'")) 


           
            js.write("['{}', {}, {}, '{}'],".format(writableCluster,avgLat,avgLon,label))
        js.write('];')
        js.close()
        
if __name__ == "__main__":
    ner = EventDetectiveNer()
    ner.loadClassifier()
    ner.generateMarkers()