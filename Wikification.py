'''Wikifies given cluster'''

from collections import Counter
import re

class Wikification:	
	def __init__(self, events):
		self.events = list(events)
		self.wikifi()
	
	def wikifi(self):
		events = []
		for tweets, label in self.events:
			ngrams = []
			for ngram, score in self.ngrams(tweets,3).most_common(50):			
				ngrams.append((' '.join(ngram)))
			events.append((tweets, label, " ".join(ngrams)))
		return events

	def eventDict(self):
		return defaultdict(list)

	def getWiki(self):
		return self.wikifi()

	def ngrams(self, tweets, n):
		ngrams = Counter()
		
		for iteration in range(n):
			for tweet in tweets:
				ngrams.update(zip(*[self.prepareTokens(tweet['text'])[i:] for i in range(iteration)]))
		return ngrams

	def prepareTokens(self, tweet):
		returnList = []
		tweet = re.sub(r"(\w)([A-Z])", r"\1 \2", tweet)
		tweet = re.sub('[!@#$.,?]', '', tweet)
		tweet = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE)

		for token in tweet.split():
			returnList.append(token)
		return returnList