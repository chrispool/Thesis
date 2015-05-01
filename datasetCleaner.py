import sys, os, json


forbidden_words = ['http']

def main():
	dataSets = os.listdir('data/')
	for i, dataset in enumerate(dataSets):
		print("{}: {}".format(i, dataset))
	choice = int(input("Select dataset: "))
    
	with open("data/" + dataSets[choice] + "/sanitizedEventCandidates.json") as jsonFile:
		candidates = json.load(jsonFile)


	for geohash in candidates:
		for timestamp in candidates[geohash]:
			#wat willen we precies doen? Filteren van woorden die beginnen met % en het woord http
			for i,tweet in enumerate(candidates[geohash][timestamp]):
				tokens = [token for token in tweet['tokens'][:] if filterToken(token)]
				candidates[geohash][timestamp][i]['tokens'] = tokens 
    
	
	with open("data/" + dataSets[choice] + "/sanitizedEventCandidates_cleaned.json", 'w') as jsonFile:
		json.dump(candidates, jsonFile)

				
def filterToken(token):
	if not '%' in token[0] and token not in forbidden_words:
		return True		
						

main()
