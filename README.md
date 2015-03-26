# Thesis
Run geo.py geotweets.txt om alle clusters te berekenen. duurt bij mij ongeveer 15 minuten... :(

Vervolgens staan in de map clusters/ alle clusters met als filename de geohash (dus geografische cluster) en de Unix timestamp. In het tekstbestand staan vervolgens de tweets die bij dat cluster horen.
Ook wordt het bestand markers.js geupdate, deze wordt ingelezen door map.html die je in je browser kan openenen en alle clusters op een kaart plot. Als je inzoomt op een cluster kan je op de verschillende tweets klikken om te lezen waar de tweet over gaat.


Om data te verzamelen:
s2816539@karora:/net/corpora/twitter2/Tweets/2015/03$ zcat 20150325???.out.gz | /net/corpora/twitter2/tools/tweet2tab -i text coordinates user date > /home/s2816539/Documents/25march.txt
