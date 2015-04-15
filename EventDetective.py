#!/usr/bin/python3

"""
##############
EventDetective
##############
Detecteert events gegeven dataset
"""
import os, json

class EventDetective:
  
	def __init__(self):
		self.dataSets = os.listdir('data/')
		self.loadDataSet()
		self.selectEvents()

	def loadDataSet(self):
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
		print(self.candidates['u1kchfe'])   

EventDetective = EventDetective()