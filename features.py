'''functions to extract features'''
from collections import Counter
from math import log, log2

def wordOverlap(candidate):
    types = Counter()
    tokens = Counter()
    n = len(candidate)
    for row in candidate:    
        types.update(set(row['tokens']))
        tokens.update(row['tokens'])  
    
    #calculate cluster IDF, hoe waardevol is woord in cluster
    for token in tokens:   
        tokens[token] = log(len(tokens)/tokens[token])  
        if token[0] == '#':
            tokens[token] *= 5
    
    maxscore = 0
    score = 0
    for t in types:
        maxscore += n * tokens[t]
        if types[t] > 1: #ignore if only in one tweet
            score += types[t] * tokens[t]
    if score == 0:
        return 0
    else:
        s = log2( (score / n) )
        return round(s * 2) / 2 #round to 0.5
 

def wordOverlapDisplay(candidate):
    types = Counter()
    tokens = Counter()
    n = len(candidate)
    for row in candidate:    
        types.update(set(row['tokens']))
        tokens.update(row['tokens'])  
    
    #calculate cluster IDF, hoe waardevol is woord in cluster
    for token in tokens:   
        tokens[token] = log(len(tokens)/tokens[token])  
        if token[0] == '#':
            tokens[token] *= 5
    
    maxscore = 0
    score = 0
    for t in types:
        maxscore += n * tokens[t]
        if types[t] > 1: #ignore if only in one tweet
            score += types[t] * tokens[t]
    if score == 0 or n == 0:
        return 0
    else:
        s =  (score / n) 
        value = round(s * 2) / 2 #round to 0.5
        common = [w + "(" + str(tokens[w]) + str(c * types[t]) + ")" for w,c in types.most_common(3)]
        return "Score: {:.2f} , Overlapping words: {} ".format( value, ' '.join(common ))   
        

def atRatio(candidate):
    #Number of @s relative to the number of posts in the cluster.
    nAt = 0
    for tweet in candidate:
        for word in tweet['text']:
            if word[0] == '@':
                nAt += 1
    return round(nAt / nTweets(candidate), 1)

def uniqueUsers(cluster):
    users = [tweet['user'] for tweet in cluster]
    return (len(set(users)))

def nTweets(cluster):
    return (len(cluster))