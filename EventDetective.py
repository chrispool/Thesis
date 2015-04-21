#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""
import os, sys, msgpack, time
from TweetPreprocessor import TweetPreprocessor
from ClusterCreator import ClusterCreator
from ClusterMerger import ClusterMerger

class EventDetective:

    def __init__(self, tweetFile):
        # zijn het idf-dictionary en de event candidates al eerder gemaakt?
        #idf = self.__load_file("idf.bin")
        #eventCandidates = self.__load_file("eventCandidates.bin")
        
        # maak of leeg de map met clusters
        self.__emptyClusterFolder()
        # preprocess tweets in tweetFile
        preprocessor = TweetPreprocessor(tweetFile)
        #idf = preprocessor.getIdf()
        tweetDicts = preprocessor.getTweetDicts()
        # maak candidate clusters
        creator = ClusterCreator(tweetDicts)
        clusters = creator.getClusters()
        # voeg candidate clusters samen tot event candidates
        merger = ClusterMerger(clusters)
        eventCandidates = merger.getEventCandidates()
        
        """n = 50
        print("\n### A selection of events candidates ###\n")
        count = 0
        for geohash in eventCandidates:
            for times in eventCandidates[geohash]:
                for tweet in eventCandidates[geohash][times]:
                    print(tweet["user"], tweet["localTime"], tweet["text"])
            print()
            count += 1
            if count == n:
                break
        """

        #self.dataSets = os.listdir('data/')
        #self.loadDataSet()
        #self.selectEvents()
        
    # Laad een bestand met msgpack, we moeten nog even bepalen of we dit gaan gebruiken
    def __load_file(self, f):
        try:
            with open(f, "rb") as f:
                d = msgpack.load(f, encoding='utf-8')
                return d
        except:
            return False    

        
    def __emptyClusterFolder(self):
        if not os.path.isdir("clusters"): 
            # clustermap bestaat nog niet
            os.makedirs("clusters")
            print("Created a new cluster folder.")
        else:
            # clustermap bestaat, haal oude clusters weg
            filelist = [f for f in os.listdir("clusters/") if f.endswith(".txt")]
            for f in filelist:
                os.remove('clusters/' + f)
            print("Emptied the cluster folder.")

    def loadDataSet(self):
        pass
        
        """for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        #todo, wat als je verkeerde dataset opgeeft..		
        jsonFile =  open("data/" + self.dataSets[choice] + "/annotation.json")
        self.annotation = json.load(jsonFile)

        jsonFile =  open("data/" + self.dataSets[choice] + "/eventCandidates.json")
        self.candidates = json.load(jsonFile)
        """

    def classifyEvents(self):
        pass

    def generateGoogleMap(self):
        pass

    def calculatePrecisionRecall(self):
        pass

    def selectEvents(self):
        pass#print(self.candidates['u1kchfe'])   
        
    """Dit moet nog even verwerkt worden...
                
        # zijn het idf-dictionary en de tweet dictionaries al eerder gemaakt?
        idf = self.__load_file("idf.bin")
        tweetDicts = self.__load_file("tweetdicts.bin")
        
        if idf and "%FILENAME%:" + tweetFile in idf and tweetDicts:
            print("Successfully loaded the earlier generated binary files for ", tweetFile, "!", sep = "")
            return tweetDicts, idf
                print("Done! Dumping dictionaries to disk...")
                
        with open('idf.bin', 'wb') as f:
            idf["%FILENAME%:" + tweetFile] = 1
            msgpack.dump(idf, f)
        print("* idf.bin is ready...")
        
        with open('tweetdicts.bin', 'wb') as f:
            msgpack.dump(tweetDicts, f)
        print("* tweetdicts.bin is ready...")
        
        # IDF DUMP
        for word in tokens:
            idf[word] += 1

        # bereken idf-score voor ieder woord
        n = len(idf)
        for word in idf:
            idf[word] = math.log10(n / idf[word])
        """

# DEMO
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./EventDetective.py tweetFile")
        sys.exit()
    start = time.time()
    detective = EventDetective(sys.argv[1])
    end = time.time() - start
    print("Took", end, "seconds.")