# Thesis

Interesting links:

http://www.movable-type.co.uk/scripts/geohash.html


Om tweets met coördinaten te verzamelen:

`zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -i text coordinates user date | python3 get_geotweets.py > march27.txt`

Hetzelfde met grep:

`zcat /net/corpora/twitter2/Tweets/2015/03/20150327???.out.gz | /net/corpora/twitter2/tools/tweet2tab -k text coordinates user date | grep -P "^[^\t]+\t[^\t]+" > march27.txt`
