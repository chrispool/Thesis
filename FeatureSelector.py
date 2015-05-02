
"""
###############
FeatureSelector
###############
"""

from collections import Counter, defaultdict
from math import log, log2
from modules import geohash
from sklearn.naive_bayes import MultinomialNB
from nltk.classify.scikitlearn import SklearnClassifier

class FeatureSelector:
    
    def __init__(self, eventCandidates):
        self.candidates = eventCandidates
        self.idf = Counter()
        self.calculateIDF()
        self.createFeatureTypes()
        
    def calculateIDF(self):
        n = 0        
        for geohash in self.candidates:
            for timestamp in self.candidates[geohash]:
                # een tweet is een document (niet een cluster)
                for tweet in self.candidates[geohash][timestamp]:
                    self.idf.update(set(tweet['tokens']))
                    n += 1
        for word in self.idf:
            self.idf[word] = log(n/self.idf[word])   
        
    def createFeatureTypes(self):
        '''get all possible word features'''
        featureTypes = Counter()
        for g in self.candidates:
            for t in self.candidates[g]:
                candidate = self.candidates[g][t]
                for row in candidate:
                    featureTypes.update(row['tokens'])
        
        for f in featureTypes:
            featureTypes[f] = featureTypes[f] * self.idf[f]

        self.features = [word for word, n in featureTypes.most_common(800)]
    
    def wordFeatureSelector(self, candidate):
        candidateFeatures = {}
        for tweet in candidate:
            for feature in self.features:
                if feature in tweet['tokens']:
                    candidateFeatures[feature] = True
                else:
                    if feature not in candidateFeatures:
                        candidateFeatures[feature] = False
                        
        return candidateFeatures     

    # de categorie classifier is nodig voor de category feature
    def featureSelector(self, cluster, classifierCat):
        featuresDict = {}
        #featuresDict['overlap'] = self._wordOverlap(cluster)
        #featuresDict['overlapSimple'] = self._wordOverlapSimple(cluster)
        featuresDict['overlapUser'] = self._wordOverlapUser(cluster)
        #featuresDict['nUsers'] = self._uniqueUsers(cluster)
        #featuresDict['nTweets'] = self._nTweets(cluster)
        #featuresDict['atRatio'] = self._atRatio(cluster) 
        featuresDict['overlapHashtags'] = self._overlapHashtags(cluster)
        #featuresDict['averageTfIdf'] = self._averageTfIdf(cluster, self.idf)
        featuresDict['category'] = classifierCat.classify(self.wordFeatureSelector(cluster))
        featuresDict['location'] = self._location(cluster) # locatie maakt niet heel veel uit
        
        return featuresDict

    def _wordOverlapUser(self, candidate):
        '''Calculate the overlap of features among users, high score when high idf types are in each tweet'''
        userTypes = defaultdict(list)
        types = Counter()

        for row in candidate:
            userTypes[row['user']].extend(row['tokens'])
        
        for user in userTypes:
            types.update(set(userTypes[user]))
        score = 0
        for t in types:
            if types[t] > 1: #ignore if only in one tweet
                if t[0] == '#':
                    score += (types[t] * 2)
                else:
                    score += types[t]

        if score > 1:
            s = log(float(score) * float(len(userTypes.keys()) )) 
            #return round((score * 2) / len(candidate))
            return round((s / len(candidate) )* 2 ) /2 
        else:
            return 0.0

    def _wordOverlapSimple(self, candidate):
        types = Counter()
        for row in candidate:
            types.update(set(row['tokens']))
        score = 0
        for t in types:
            if types[t] > 1:
                if t[0] == '#':
                    score += (types[t] * 2)
                else:
                    score += types[t]

        return round((score / len(candidate)) * 2) / 2

    def _wordOverlap(self, candidate):
        types = Counter() #counter with n of tweets this term occurs
        tokens = Counter()
        idf = defaultdict(float)
        n = len(candidate)
        for row in candidate:    
            types.update(set(row['tokens']))
            tokens.update(row['tokens'])  
        #calculate cluster IDF, hoe waardevol is woord in cluster
        #IDF(t) = log_e(Total number of documents / Number of documents with term t in it).   
        for t in types:
            idf[t] += log(n/types[t]) 
            if t[0] == '#':
                idf[t] *= 3
        
        score = 0
        for t in types:
            if types[t] > 1: #ignore if only in one tweet
                score += types[t] * idf[t]
        
        if score == 0:
            return 0
        else:
            return round((score / n) * 2) / 2 # round to 0.5
    
    def _overlapHashtags(self, candidate):
        #find all hashtags
        h = []
        hashTagsC = Counter()
        for tweet in candidate:
            for token in tweet['tokens']:
                if token[0] == '#':
                    hashTagsC[token] += 1

        return round((sum(hashTagsC.values()) / len(candidate)) * 2 ) / 2

    def _retweets(self, candidate):
        #feature to negative score retweet clusters
        pass

    def _wordOverlapDisplay(self, candidate):
        types = Counter() #counter with n of tweets this term occurs
        tokens = Counter()
        idf = defaultdict(float)
        n = len(candidate)
        for row in candidate:    
            types.update(set(row['tokens']))
            tokens.update(row['tokens'])  
        
        #calculate cluster IDF, hoe waardevol is woord in cluster
        #IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
        
        for t in types:
            idf[t] += log(n/types[t]) 
            if t[0] == '#':
                idf[t] *= 3
        maxscore = 0
        score = 0
        for t in types:
            maxscore += n * tokens[t]
            if types[t] > 1: #ignore if only in one tweet
                score += types[t] * idf[t]
        if score == 0 or n == 0:
            return 0
        else:
            
            value = round((score / n) * 2) / 2 #round to 0.5
            common = [w + "(" + str(tokens[w]) + str(c * idf[t]) + ")" for w,c in types.most_common(3)]
            return "Score: {:.2f} , Overlapping words: {} ".format( value, ' '.join(common ))   
            
    def _atRatio(self, candidate):
        #Number of @s relative to the number of posts in the cluster.
        nAt = 0
        for tweet in candidate:
            for word in tweet['text']:
                if word[0] == '@':
                    nAt += 1
        return round(nAt / nTweets(candidate), 2)

    # Bepaal de gemiddelde locatie (lengte- en breedtegraad, omgezet
    # naar geohash) van alle gebruikers in een cluster
    def _location(self, candidate):
        avgLon = 0
        avgLat = 0
        
        for tweet in candidate:
            avgLon += float(tweet["lon"])
            avgLat += float(tweet["lat"])
            
        avgLon /= len(candidate)
        avgLat /= len(candidate)
        
        return geohash.encode(avgLat, avgLon, 6)

    def _uniqueUsers(self, cluster):
        users = [tweet['user'] for tweet in cluster]
        return round(  len( set( users)) , 1 )

    def _nTweets(self, cluster):
        return (len(cluster))

    def _averageTfIdf(self, candidate, idf):
        tokens = Counter()
        for tweet in candidate:
            tokens.update(tweet['tokens'])

        score = 0
        for token in tokens:
            score += tokens[token] * idf[token]
            
        return score / len(candidate)