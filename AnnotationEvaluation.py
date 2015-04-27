#!/usr/bin/python3

"""
 Computes the kappa score for annotators and keeps only the annotations (and
 their event candidates) about which the annotators agree.
"""

import os,sys

class AnnotationEvaluation:
    
    def __init__(self):
        self.dataSets = os.listdir('data/')
        self.annotation1 = {}
        self.annotation2 = {}
        self._loadAnnotations()
        
    def _loadAnnotations(self):
        for i, dataset in enumerate(self.dataSets):
            print("{}: {}".format(i, dataset))
        choice = int(input("Select dataset: "))
        
        self.datasetName = self.dataSets[choice]
        
        fnames = []
        # kijk of bestanden in data/gekozenDataSet beginnen met /annotation_
        for f in os.listdir("data/" + self.dataSets[choice]):
            if f.startswith("/annotation_"):
                fnames.append(f)
                
        if len(fnames) != 2:
            print("Sorry, this script will only work for two annotators.")
            sys.exit()
        
        self.annotation1 = open("data/" + self.dataSets[choice] + fname[0])
        self.annotation2 = open("data/" + self.dataSets[choice] + fname[0])
        self.candidates = json.load(jsonFile)
        
if __name__ == "__main__":
    AnnotationEvaluation()