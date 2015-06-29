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
`DEVTEST` dataset.

### Time for the detective

All right, now you are ready to detect some events for a new dataset of tweets, and visualize those events on a
map! If you have created a dataset containing new event candidates with `EventCandidates`, run

`./EventDetective.py`

and first select the `DEVTEST` dataset with your trained classifiers and then the new dataset. 

And now... have a look at `vis/map/chart.html` and watch the magic ^_^

<!--
VOORBEELDCOMMANDO'S (Of zie Listing 1 van "scriptie David de Kleer/scriptie.pdf")

# Voor de volgende commando's wordt aangenomen dat een gebruiker in de hoofdmap van de
# repository https://github.com/chrispool/Thesis is en de toegang heeft tot de Karora−
# server van de Rijksuniversiteit Groningen.
Chris_Thesis$ cd corpus/

# verbinden met Karora
Chris_Thesis/corpus$ ssh s_of_p_nummer@bastion.service.rug.nl
bastion:~$ ssh s_of_p_nummer@karora.let.rug.nl

# "speelgoed"−traindata (tweets van 10 juni) verzamelen
karora:~$ zcat /net/corpora/twitter2/Tweets/2015/06/20150610???.out.gz | /net/corpora/twitter2/
tools/tweet2tab −i text coordinates user date | grep −P "^[^\t]+\t[^\t]+" > june10_train.txt

# "speelgoed"−testdata (tweets van 11 juni) verzamelen
karora:~$ zcat /net/corpora/twitter2/Tweets/2015/06/20150611???.out.gz | /net/corpora/twitter2/
tools/tweet2tab −i text coordinates user date | grep −P "^[^\t]+\t[^\t]+" > june11_test.txt

# zet de data over naar eigen computer
karora:~$ exit
bastion:~$ sftp s_of_p_nummer@karora.let.rug.nl
sftp> get june10_train.txt
sftp> get june11_test.txt
sftp> exit
bastion:~$ exit
Chris_Thesis/corpus$ sftp s_of_p_nummer@bastion.service.rug.nl
sftp> get june10_train.txt
sftp> get june11_test.txt
sftp> exit
Chris_Thesis/corpus$ cd ..

# event candidates van corpus/june10_train.txt verzamelen in een dataset genaamd june10
Chris_Thesis$ ./EventCandidates.py corpus/june10_train.txt june10

# event candidates van corpus/june11_test.txt verzamelen in een dataset genaamd june11
Chris_Thesis$ ./EventCandidates.py corpus/june11_test.txt june11

# Annoteren voor annotator David. Voer het nummer van dataset june10 in, daarna voor iedere
# event candidate het nummer van de categorie waar deze het beste onder past.
#
# Herhaal annotatie voor de testset en voer eerst het nummer van dataset june11 in.
#
# Wanneer er sprake is van twee annotatoren moet de annotatie vanzelfsprekend worden
# herhaald voor een andere annotator, en moet vervolgens ./AnnotationEvaluation.py
# worden uitgevoerd (voor de kappa−score en het samenvoegen van de annotaties).
Chris_Thesis$ ./Annotator.py David

# DEVTEST met de trainset (willekeurige 80/20 split), voer het nummer van dataset june10 in.
Chris_Thesis$ ./ClassifierCreator.py

# TEST met de train− en testset. Voer de nummers van dataset june10 (trainset) in om te trainen
# en het nummer van dataset june11 (testset) om te testen. De classifiers worden weggeschreven
# naar data/june10/categoryClassifier.bin en data/june10/eventClassifier.bin.
Chris_Thesis$ ./ClassifierCreator.py −test

# Nu kunnen events worden gedetecteerd met EventDetective.py (gewone Google Map met markers)
# OF EventDetectiveChart.py (Google Map met markers en staafdiagram). Voer eerst het nummer
# van dataset june10 in, vervolgens het nummer van een dataset met event candidates.
Chris_Thesis$ ./EventDetective (of ./EventDetectiveChart.py)

# Open /vis/map/map.html voor een visualisatie van de gedetecteerde events.
Chris_Thesis$ firefox vis/map/map.html &
-->