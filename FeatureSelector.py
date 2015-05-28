
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
        self.featureTypes = ['wordOverlapUser', 
                            'wordOverlapSimple',
                            'wordOverlap',
                            'location', 
                            'uniqueUsers',
                            'nTweets',
                            'wordFeatures',
                            'category']
        
        self.candidates = eventCandidates
        self.idf = Counter()
        self.calculateIDF()
        self._createFeatureTypes()
        
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
        
    def _createFeatureTypes(self):
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
    
    def _wordFeatures(self, candidate):
        candidateFeatures = {}
        for tweet in candidate:
            for feature in self.features:
                if feature in tweet['tokens']:
                    candidateFeatures[feature] = True
                else:
                    if feature not in candidateFeatures:
                        candidateFeatures[feature] = False
                        
        return candidateFeatures
    
    def addCategoryClassifier(self, classifierCat):
        self.classifierCat = classifierCat

    def getFeatures(self, candidate, features):
        returnFeatures = {}
        for feature in features:
            if feature in self.featureTypes:
                method = getattr(self, "_" + feature)
                if feature == 'wordFeatures':
                    wordFeatures = method(candidate)
                    #add word features to dictionary to be able to combine features
                    for key in wordFeatures:
                        returnFeatures[key] = wordFeatures[key]
                else:
                    returnFeatures[feature] = method(candidate)
            else:
                print("The feature", feature, "is not available.")

        return returnFeatures

    def _wordOverlapUser(self, candidate):
        '''Calculate the overlap of features among users, high score when df value for a type is high'''
        userTypes = defaultdict(list)
        types = Counter()

        for row in candidate:
            userTypes[row['user']].extend(row['tokens'])
        
        for user in userTypes:
            types.update(set(userTypes[user]))
        score = 0
        for t in types:
            if types[t] > 1: # ignore if type occurs only in one tweet
                if t[0] == '#':
                    score += (types[t] * 2)
                else:
                    score += types[t]

        if score > 1:
            s = log(score * len(userTypes.keys()))
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
        types = Counter() # counter with n of tweets this term occurs
        idf = defaultdict(float)
        n = len(candidate)
        for row in candidate:
            types.update(set(row['tokens']))
        # calculate cluster IDF, hoe waardevol is woord in cluster
        # IDF(t) = log(Total number of documents / Number of documents with term t in it).   
        for t in types:
            idf[t] += log(n/types[t]) 
            if t[0] == '#':
                idf[t] *= 3
        
        score = 0
        for t in types:
            if types[t] > 1: # ignore if type occurs only in one tweet
                score += types[t] * idf[t]
        
        if score == 0:
            return 0
        else:
            return round((score / n) * 2) / 2 # round to 0.5

    def _location(self, candidate):
        """Bepaal de gemiddelde locatie (lengte- en breedtegraad, omgezet
        naar geohash) van alle gebruikers in een cluster."""
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
        return len(set(users))

    def _nTweets(self, cluster):
        return len(cluster)
    
    def _category(self, candidate):
        return self.classifierCat.classify(self._wordFeatures(candidate))
