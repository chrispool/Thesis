# Thesis

Interessante links:

- <b>NLTK en Scikit Learn combineren?</b> http://www.quora.com/How-can-I-preprocess-labeled-data-for-use-with-SciKit-Learn
http://stackoverflow.com/questions/11460115/nltk-multiple-feature-sets-in-one-classifier
- GeoHash (precision, neighbours): http://www.movable-type.co.uk/scripts/geohash.html
- Scikit Learn Tutorial: http://scikit-learn.org/stable/tutorial/basic/tutorial.html#loading-an-example-dataset
- Working with text data: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html#exercise-2-sentiment-analysis-on-movie-reviews
- Text Feature Extraction, hoe tekst kan worden omgezet naar numerieke representatie in Scikit Learn (zie ook de links naar voorbeelden die worden genoemd): http://scikit-learn.org/dev/modules/feature_extraction.html#text-feature-extraction
- Het gebruik van een pipeline om de optimale waardes voor features te vinden: http://scikit-learn.org/dev/auto_examples/model_selection/grid_search_text_feature_extraction.html#example-model-selection-grid-search-text-feature-extraction-py
- Train-test split: http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.train_test_split.html#sklearn.cross_validation.train_test_split

Om tweets met coördinaten te verzamelen:

`zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -i text coordinates user date | python3 get_geotweets.py > march27.txt`

Hetzelfde met grep:

`zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -k text coordinates user date | grep -P "^[^\t]+\t[^\t]+" > march27.txt`
