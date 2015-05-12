#!/usr/bin/env python3

import subprocess
from EventDetective import EventDetective
from operator import itemgetter
from collections import defaultdict, Counter

class EventDetectiveChart(EventDetective):
    
    def simTweetsWithoutLocation(self):
        tweetList = []
        with open('corpus/5mei_all.txt', 'r') as f:
            for line in f:
                tweetList.append(line)
        
        for tweets,label in self.events:
            if '2015-05-05' in tweets[0]['localTime']:
                tweets = sorted(tweets, key=itemgetter('unixTime'))
                importantWords = self._getImportantWords(2,tweets)
                print(tweets)
                eventStart = tweets[0]['localTime']
                eventEnd = tweets[-1]['localTime']
                eventIntervalTweets = []
                # itereren we over het interval van huidige event?
                intervalIter = False
                        
                for tweet in tweetList:
                    if intervalIter:
                        wordCount = 0
                        for word,n in importantWords:
                            if word in tweet:
                                wordCount += 1
                        if wordCount > 1:
                            eventIntervalTweets.append(tweet)
                            
                    if eventStart in tweet:
                        intervalIter = True
                    elif eventEnd in tweet:
                        break
                    
                tweets.extend(eventIntervalTweets)

            # TODO woorden die door meerdere gebruikers worden genoemd (meer dan 1x voorkomen)
            
            # TODO
            # find hashtags (min 2 people)
            #for tweet in tweets:
            #    for word in tweet['tokens']:
            #        if word.startswith("#")
         
    # geeft de n hoogste tf waarden
    def _getImportantWords(self, n, tweets):
        result = Counter()
        for tweet in tweets:
            result.update(tweet['tokens'])
        #reslist = list(result.keys())
        #print(reslist)
        #for word in reslist:
        #    if word.startswith('#'):
        #        del result[word]
        return(result.most_common(n))
            
    def generateMarkers(self):
        print("Creating Google Maps markers & graphs...")
        
        js = open('vis/map/js/markers.js','w')
        js.write('var locations = [')
        
        for tweets,label in self.events:
            writableCluster = ''
            gh = []
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
                
                gh.append(tweet['geoHash'])
                avgLon += float(tweet["lon"])
                avgLat += float(tweet["lat"])
                # backslashes voor multiline strings in Javascript
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text']).replace("'", "\\'")
                prevTime = tweet['unixTime']
            
            for simTweetTime in sorted(tweetSimTimeDict):
                simTweetCluster = tweetSimTimeDict[simTweetTime]
                
                # pak maximaal de 10 middelste tweets van een cluster
                if len(simTweetCluster) > 10:
                    sliceVal = len(simTweetCluster)//2
                    simTweetCluster = tweetSimTime[sliceVal-5:sliceVal+5]
                
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
            js.write("['{}', {}, {}, '{}', {}, '{}'],".format(writableCluster,avgLat,avgLon,label,plotData,subTitle))
        
        js.write('];')
        js.close()    
        
if __name__ == "__main__":
    detective = EventDetectiveChart()
    #detective.simNoGeo()
    detective.generateMarkers()