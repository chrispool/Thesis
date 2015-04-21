#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""
import os, sys, msgpack, time, json

class EventDetective:

    def __init__(self):
        self.dataSets = os.listdir('data/')
        self.__emptyClusterFolder()
        self.__loadDataSet()
        
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

    def __loadDataSet(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        #todo, wat als je verkeerde dataset opgeeft..		
        jsonFile =  open("data/" + self.dataSets[choice] + "/annotation.json")
        self.annotation = json.load(jsonFile)

        jsonFile =  open("data/" + self.dataSets[choice] + "/eventCandidates.json")
        self.candidates = json.load(jsonFile)

    def classifyEvents(self):
        pass

    def generateGoogleMap(self):
        pass

    def calculatePrecisionRecall(self):
        pass

    def selectEvents(self):
        pass

# DEMO
if __name__ == "__main__":
    detective = EventDetective()