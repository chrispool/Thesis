#!/usr/bin/python3

# Train Naive Bayes van NLTK en MultinomialNB en SVM van Scikit Learn. NLTK maakt het echt
# een stuk simpeler ^_^

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn import grid_search
from nltk.classify.scikitlearn import SklearnClassifier
from nltk import NaiveBayesClassifier

# NLTK gebruikt SklearnClassifier als een wrapper om de Scikit Learn Machine Learning opties
SVM = SklearnClassifier(SVC())
SCI_NB = SklearnClassifier(MultinomialNB())

# featureSet is een lijst van tuples: [(features1, label1), (features2, label2), ...]
# * De features zijn dictionaries die de woorden en andere features van de tweet bevatten
# * De labels zijn categorieen (dus de event nummers in ons geval)
featureSet = [({'Dit': 1.1, 'zijn': 0.9, 'features': 0.4, "testFeature" : False}, 1), 
              ({'Dit': 1.1, 'ook': 1.0, "testFeature" : True}, 2)]

# train de NLTK Naive Bayes classifier
NLTK_NB = NaiveBayesClassifier.train(featureSet)
# train de Scikit Learn MultinomialNB Classifier
SCI_NB.train(featureSet)
# train de Scikit Learn SVM Classifier
SVM.train(featureSet)

classifier = SVM
# Even de classifier uitproberen
print(classifier.classify({"Dit":1.1, "zijn":0.9})) # 1
print(classifier.classify({"zijn" : 0.5, "Dit" : 1.1,"testFeature" : True, })) # 2

"""
# * OPTIONEEL
# TEST DIT MET MEER DATA: vind de beste parameters voor de SVM (automatisch) met GridSearch
# Weet nog niet echt zeker of dit gaat werken. Eerst maar eens zien of het uberhaupt allemaal
# werkt :-)
SVM2 = SVC()
parameters = {"kernel" : ("linear", "poly", "rbf")}
SVM_search = grid_search.GridSearchCV(SVM2, parameters, scoring="f1")
SVM_search = SklearnClassifier(SVM_search)
"""