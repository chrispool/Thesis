
from collections import Counter, defaultdict
from math import log, log2
from modules import geohash
import sys

'''Class returns feature dictionary for a given candidate'''
class Features:

    def __init__(self, candidates):
        self.featureTypes = ['wordOverlapUser', 
                            'wordOverlapSimple',
                            'wordOverlap',
                            'overlapHashtags', 
                            'atRatio', 
                            'location', 
                            'uniqueUsers',
                            'nTweets',
                            'averageTfIdf',
                            'wordFeatures',
                            'category' ]

        self.candidates = candidates
        self.createFeatureTypes()
    
    def getFeatureTypes(self):
        return self.featureTypes

    
    def createFeatureTypes(self):
        featureTypes = Counter()
        for g in self.candidates:
            for t in self.candidates[g]:
                candidate = self.candidates[g][t]
                for row in candidate:
                    featureTypes.update(row['tokens'])

        self.features = [word for word, n in featureTypes.most_common(800)]

    
    def getFeatures(self, candidate, features):
        returnFeatures = {}
        for feature in features:
            if feature in self.featureTypes:
                function = feature
                method = getattr(self, function)
                if feature == 'wordFeatures':
                    wordFeatures = method(candidate)
                    #add word features to dictionary to be able to combine features
                    for key in wordFeatures:
                        returnFeatures[key] = wordFeatures[key]
                else:
                    returnFeatures[feature] = method(candidate)
            else:
                print("Feature not available")
        return returnFeatures
    

    def addCategoryClassifier(self, classifier):
        self.classifier = classifier

    '''feature functions'''
    def wordOverlapUser(self, candidate):
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



    def __wordOverlapSimple(self, candidate):
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


    def wordOverlap(self, candidate):
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

 
    def __overlapHashtags(self, candidate):
        #find all hashtags
        h = []
        hashTagsC = Counter()
        for tweet in candidate:
            for token in tweet['tokens']:
                if token[0] == '#':
                    hashTagsC[token] += 1

        return round((sum(hashTagsC.values()) / len(candidate)) * 2 ) / 2

    
    def __retweets(self, candidate):
        #feature to negative score retweet clusters
        pass


    def __wordOverlapDisplay(candidate):
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
            

    def __atRatio(self, candidate):
        #Number of @s relative to the number of posts in the cluster.
        nAt = 0
        for tweet in candidate:
            for word in tweet['text']:
                if word[0] == '@':
                    nAt += 1
        return round(nAt / nTweets(candidate), 2)

   
    # Bepaal de gemiddelde locatie (lengte- en breedtegraad, omgezet
    # naar geohash) van alle gebruikers in een cluster
    def __location(self, candidate):
        avgLon = 0
        avgLat = 0
        
        for tweet in candidate:
            avgLon += float(tweet["lon"])
            avgLat += float(tweet["lat"])
            
        avgLon /= len(candidate)
        avgLat /= len(candidate)
        
        return geohash.encode(avgLat, avgLon, 6)

    def __uniqueUsers(cluster):
        users = [tweet['user'] for tweet in cluster]
        return round(  len( set( users)) , 1 )

    def __nTweets(cluster):
        return (len(cluster))

    def __averageTfIdf(candidate, idf):
        tokens = Counter()
        for tweet in candidate:
            tokens.update(tweet['tokens'])

        score = 0
        for token in tokens:
            score += tokens[token] * idf[token]
            
        return score / len(candidate)

    def wordFeatures(self, candidate):
        candidateFeatures = {}
        for row in candidate:
            for feature in self.features:
                if feature in row['tokens']:
                    candidateFeatures[feature] = True
                else:
                    if feature not in candidateFeatures:
                        candidateFeatures[feature] = False 
        return candidateFeatures  

    def category(self, candidate):
        return self.classifier.classify(self.wordFeatures(candidate))