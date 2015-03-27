# Thesis

Interesting links:

http://www.movable-type.co.uk/scripts/geohash.html


Om data te verzamelen:
zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -i text coordinates user date |python3 geo.py > march27.txt
