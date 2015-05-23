from nltk.tag.stanford import NERTagger 
from collections import defaultdict

class Ner():
	def __init__(self):
		classifier = "ner/classifiers/" + "ner-model-tweets.ser.gz"
		jar = "ner/stanford-ner-3.4.jar"
		self.tagger = NERTagger(classifier, jar)

	def tagText(self, candidate):
		result = defaultdict(list)
		text = " ".join([tweet['text'] for tweet in candidate]) #make one long text		
		for line in self.tagger.tag(self.tokens):
			for word, tag in line:
				result[tag].append(word)
		return result