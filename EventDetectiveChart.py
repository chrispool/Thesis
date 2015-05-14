#!/usr/bin/env python3

import subprocess
from EventDetective import EventDetective
from operator import itemgetter
from collections import defaultdict, Counter
from TweetPreprocessor import TweetPreprocessor
from math import log

class EventDetectiveChart(EventDetective):
    
    def simTweetsWithoutLocation(self):
        tweetList = []
        with open('corpus/5mei_all.txt', 'r') as f:
            for line in f:
                tweetList.append(line)
                
        for i in range(len(self.events)):
            tweets = self.events[i][0]
            label = self.events[i][1]
            eventIntervalTweets = []
            importantWords = self._getImportantWords(tweets)
            
            # PROOF OF CONCEPT voor alle tweets van 5 mei
            #############################################
            # * Bevrijdingsfestival Utrecht bij Kanaleneiland in Utrecht (ingedeeld als incident)
            # * Bevrijdingspop in Haarlem staat weergegeven als bijeenkomst in Haarlem (wordt niet
            #   iedere keer gevonden)
            # * Werkt niet goed voor [('zwolle', 47), ('nieuws', 14), ('mei', 14)], maar dit was
            #   sowieso al geen event
            if '2015-05-05' in tweets[0]['localTime']:
                tweets = sorted(tweets, key=itemgetter('unixTime'))

                eventStart = tweets[0]['localTime']
                eventEnd = tweets[-1]['localTime']
                # itereren we over het interval van huidige event?
                intervalIter = False
                        
                for tweet in tweetList:
                    if intervalIter:
                        wordCount = 0
                        for word,n in importantWords:
                            if " " + word in tweet or "#" + word in tweet or "@" + word in tweet:
                                wordCount += 1
                        if wordCount > 1:
                            # n (standaard 3) woorden moeten minstens 2 keer voorkomen
                            eventIntervalTweets.append(tweet)

                    if eventStart in tweet:
                        intervalIter = True
                    elif eventEnd in tweet:
                        break
            
            if eventIntervalTweets:
                preprocessor = TweetPreprocessor(eventIntervalTweets)
                tweetDicts = preprocessor.getTweetDicts()
                tweets.extend(tweetDicts)
            
            # titel van event: 3 meest voorkomende woorden
            eventTitle = ""
            for word,n in importantWords:
                eventTitle += word + " "
            eventTitle +=  "- " + label

            self.events[i] = (tweets,label,eventTitle)
       
    # geeft de n hoogste tf waarden
    def _getImportantWords(self, tweets, n=3):
        result = Counter()
        for tweet in tweets:
            for word in tweet['tokens']:
                if word.startswith('#') or (word.startswith('@') and word[1:] in result):
                    # hashtag-termen zijn belangrijk, ze tellen dubbel
                    result[word[1:]] += 2
                else:
                    result[word] += 1
        return(result.most_common(n))
            
    def generateMarkers(self):
        print("Creating Google Maps markers & graphs...")
        
        js = open('vis/map/js/markers.js','w')
        js.write('var locations = [')
        
        for tweets,label,eventTitle in self.events:
            writableCluster = ''
            i = 0
            avgLon = 0
            avgLat = 0
            tweets = sorted(tweets, key=itemgetter('unixTime'))
            plotData = '['
            prevTime = 0
            tweetSimTimeDict = defaultdict(list)
            
            for tweet in tweets:
                i += 1
                
                # t is de unix time afgerond op twee minuten (integerdeling met 120 en dat * 120)
                t = (tweet['unixTime']//120) * 120
                tweetSimTimeDict[t].append(tweet)
                tweetText = tweet['text'].replace("'", "\\'")
                if 'geoHash' in tweet:
                    # tweets MET coordinaten
                    gh = tweet['geoHash']
                    avgLon += float(tweet["lon"])
                    avgLat += float(tweet["lat"])
                else:
                    # tweets ZONDER coordinaten
                    gh = ""
                    i -= 1 # deze tweets tellen dus ook niet mee voor de gemiddelde positie!
                    tweetText = "<b>" + tweetText + "</b>"
                    
                # backslashes voor multiline strings in Javascript
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], gh, tweet['user'], tweetText)
                prevTime = tweet['unixTime']
            
            for simTweetTime in sorted(tweetSimTimeDict):
                simTweetCluster = tweetSimTimeDict[simTweetTime]
                
                # pak maximaal de 10 middelste tweets van een cluster
                if len(simTweetCluster) > 10:
                    sliceVal = len(simTweetCluster)//2
                    simTweetCluster = simTweetCluster[sliceVal-5:sliceVal+5]
                
                # tekst van tweets samenvoegen
                tweetText = ""
                for simTimeTweet in simTweetCluster:
                    tweetText += simTimeTweet['text'].replace("'", "\\'")
                    # check of dit niet de laatste tweet is: voeg dan newline toe tussen tweets
                    if simTimeTweet != simTweetCluster[-1]:
                        tweetText += "<br/><br/>"
                        
                plotData += "{"
                plotData += "x:new Date({}*1000),y:{},tweetData:'{}'".format(simTweetTime,len(simTweetCluster),tweetText)
                plotData += "},"
                
            # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
            # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
            # Oftewel, we doen even alsof de aarde plat is ;-)
            avgLon /= i
            avgLat /= i
            plotData += ']'
            # subTitle is de subtitle van de grafiek
            subTitle = tweets[-1]['localTime'].split()[0]
            js.write("['{}', {}, {}, '{}', {}, '{}', '{}'],".format(writableCluster,avgLat,avgLon,label,plotData,subTitle,eventTitle))
        
        js.write('];')
        js.close()    
        
if __name__ == "__main__":
    detective = EventDetectiveChart()
    detective.simTweetsWithoutLocation()
    detective.generateMarkers()