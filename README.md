# EventDetective

This is a system for event detection in Twitter. It was (mainly) written in Python by Chris Pool and David de 
Kleer for our bachelor project. You can find our accompanying theses in the folders *scriptie Chris Pool* 
(English) and *scriptie David de Kleer* (Dutch). Now, we will describe how to run a basic experiment with our software.

## How to get the basic event detection running

### Gather some tweets

First, you will need to gather tweets in the following format (use tab characters as seperator):

`Nobody expects the Spanish Inquisition!<tab>latitude longitude<tab>mpython<tab>2015-03-27 00:01:17 CET Fri`

If you are able to access the Karora machine of the University of Groningen, you can run the following 
command (via `ssh`) on this machine for an easy way to gather tweets in this format:

`zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -k text coordinates user date | grep -P "^[^\t]+\t[^\t]+" > march27.txt`

This command gathers all the tweets with geo-information for 27 March 2015 and puts them in the file `march27.txt`.
If you do not have access to Karora, you will need to extract tweets from the Twitter Stream yourself. Otherwise,
you can always test with some corpora we've gathered for training and testing our system (only Dutch tweets!),
for example `corpus/27maart.txt`.

### Line up the event candidates

The next step is to transform your data into a dataset of *event candidates* (possible events). To store the event 
candidates for March (let's take the file `corpus/maart.txt`) in a dataset called `maart` you can use:

`./EventCandidates.py corpus/maart.txt maart`

### Tedious annotation

Because we take a *supervised learning* approach in this system you will now need to annotate data manually. If
you want to annotate some data you can use 

`./Annotator.py name-judge`

to annotate your data. If you have been annotating with two people, you can evaluate your annotations with

`./AnnotationEvaluation.py`

For the people just interested in Dutch tweets: we've already gone through the hard work of manually annotating 
about 1500 event candidates for March 2015. 

### Train those classifiers!

If you are done annotating, take a deep breath and start training classifiers. Just run

`./ClassifierCreator.py -test`

and select a dataset with event candidates and annotations. An important note is that you will need two datasets
to be able to save the actual classifiers (or whatever, just cheat and remove `if self.realTest:` on line 53): one to train
(your `DEVTEST` dataset) and one to test (your `TEST` dataset). The classifiers will be saved in the folder of the 
selected dataset.

### Time for the detective

All right, now you are ready to detect some events for a new dataset of tweets, and visualize those events on a
map! If you have created a dataset containing new event candidates with `EventCandidates`, run

`./EventDetective.py`

and first select the dataset with your trained classifiers and then the new dataset. 

And now... have a look at `vis/map/chart.html` and watch the magic ^_^
