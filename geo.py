import sys
import geohash
from collections import defaultdict
from collections import Counter
import math
import time
import datetime
from operator import itemgetter


def main(argv):
	
	'''settings'''
	minutes = 120
	nTweets = 2
	hashAccuracy = 6
	

	clusters = defaultdict(list)
	
	js = open('markers.js','w')
	js.write(' var locations = [')
	
	n = 0
	for line in open(argv[1]):
		n += 1
		elements = line.strip().split('\t')
		coord = elements[1].split()
		
		geoH = geohash.encode(float(coord[1]),float(coord[0]),8)[:hashAccuracy]
		s = ' '.join(elements[3].split()[:2])
		ts = int(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple()))
		

		key = (geoH, ts)
		for k in clusters.keys():
			if k[0] == geoH:
				if k[1] <= ts <= (k[1] + (minutes*60)):
					key = (geoH, k[1])			
				
		clusters[key].append(elements) # create new cluster
	
	i = 1


	'''loop door clusters om te kijken wat event candidates zijn'''
	for cl in clusters.keys():
		val = list(clusters[cl])
		timeCluster = defaultdict(list)

		userlist = []
		geolist = []

		if len(val) > nTweets: #als cluster meer dan nTweets bevat
			for element in clusters[cl]:
				if not element[2] in userlist: #toeveogen aan lijst met unieke users van dit cluster
					userlist.append(element[2])
				if not element[1] in geolist: #toeveogen aan lijst met unieke locaties van dit cluster
					geolist.append(element[1])
	
		if len(userlist) > 1 and len(geolist) > 1: # als er meer dan 1 unieke gebruikers en lcoaties zijn pas weergeven
				f = open('clusters/' + cl[0] + '-' + str(cl[1]) + '.txt','w')
				for element in clusters[cl]:
					i = i + 1
					coord = element[1].split()
					'''textfiles maken van alle afzonderlijke clusters en JS file maken voor Google map'''
					f.write("{}, {}, {}, {} \n".format(element[2], element[0].replace("'", ""), ', '.join(reversed(coord)), element[3])) 
					js.write("['{} {}', {}, {}, {}]\n".format(element[2],element[3], element[0].replace("'", ""), ', '.join(reversed(coord)), i))
				f.close()

	js.write('];')
	js.close()			

		
	
	
	


	

main(sys.argv)