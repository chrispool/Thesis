'''Wikifies given cluster'''

from collections import Counter
import re
import nltk
from nltk.collocations import *

class Wikification:	
	def __init__(self, events):
		self.stoplist = []
		with open("corpus/stopwords.txt") as stopwords:
			for stopword in stopwords:
				self.stoplist.append(stopword.strip())
		self.stoplist.extend(['http', 'het'])
		self.events = list(events)
		self.wikifi()
	
	def wikifi(self):
		events = []
		
		bigram_measures = nltk.collocations.BigramAssocMeasures()

		for candidates, label in self.events:
			tweets = ""
			for candidate in candidates:
				tweets += " "+ candidate['text'] 		
			tokens = self.tokenize(tweets)
			finder = BigramCollocationFinder.from_words(tokens)
			string = ""
			finder.apply_freq_filter(3)
			for firstword, secondword in finder.nbest(bigram_measures.pmi, 10):
				string += " {} {} ".format(firstword, secondword)
			#ngrams = []
			#for ngram, score in self.ngrams(tweets,3).most_common(50):			
				#ngrams.append((' '.join(ngram)))

			events.append((candidates, label, str(string)))
		return events



	def tokenize(self, string):
		string = re.sub(r'^https?:\/\/.*[\r\n]*', '', string, flags=re.MULTILINE)
		string = re.sub('[!@#$.,?]', '', string)
		string = self.convert(string)
		returnList = [token for token in string.split() if token not in self.stoplist and len(token) > 2 and token.isalpha() ]
		return returnList

	def convert(self, token):
	    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', token)
	    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()

	def eventDict(self):
		return defaultdict(list)

	def getWiki(self):
		return self.wikifi()

	def ngrams(self, tweets, n):
		ngrams = Counter()	
		for iteration in range(n):
			for tweet in tweets:
				ngram = zip(*[self.prepareTokens(tweet['text'])[i:] for i in range(iteration)])
				ngramFiltered = [token for token in ngram if token not in self.stoplist]
				ngrams.update(ngramFiltered)
		return ngrams

	def prepareTokens(self, tweet):

	
		return tweet.split()