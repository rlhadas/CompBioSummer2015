# MasterReconciliation.py
# Juliet Forman, Srinidhi Srinivasan, Annalise Schweickart, and Carter Slocum
# July 2015

# This file contains functions for computing maximum parsimony 
# DTL reconciliations using the edge-based DP algorithm.  The main # # function in this file is called Reconcile and the remaining 
# functions are helper functions that are used by Reconcile.



import DP
import HeyJuliet
import newickToVis
import ReconConversion
import orderGraph
import newickFormatReader
import ReconciliationGraph
from sys import argv
import copy
import calcCostscapeScore

def Reconcile(argList):
	"""Takes command-line arguments of File, costs, and amount of desired reconciliations. Creates Files for 
	the host, parasite, and reconciliations"""
	fileName = argList[1]
	D = float(argList[2])
	T = float(argList[3])
	L = float(argList[4])
	freqType = argList[5]
	switchLo = float(argList[6])
	switchHi = float(argList[7])
	lossLo = float(argList[8])
	lossHi = float(argList[9])
	orderedGraphs = []
	host, paras, phi = newickFormatReader.getInput(fileName)
	hostRoot = findRoot(host)
	hostv = treeFormat(host)
	hostOrder = orderGraph.date(hostv)
	hostBranchs = branch(hostv, hostOrder)
	if freqType == "Frequency":
		DTL, numRecon = DP.DP(host, paras, phi, D, T, L)
	elif freqType == "xscape":
		DTL = calcCostscapeScore.newScoreWrapper(fileName, switchLo, switchHi, lossLo, lossHi, D, T, L)
	elif freqType == "unit":
		DTL = unitScoreDTL(host, paras, phi, D, T, L)
	DTLGraph = copy.deepcopy(DTL)
	scoresList, rec = HeyJuliet.Greedy(DTL, paras)
	graph = []
	for item in rec:
		graph.append(ReconciliationGraph.buildReconstruction(host, paras, item))
	for item in range(len(graph)):
			orderedGraphs += orderGraph.date(graph[item])
			ReconConversion.convert(rec[item], DTLGraph, paras, fileName[:-7], item)
	newickToVis.convert(fileName,hostBranchs)

def unitScoreDTL(hostTree, parasiteTree, phi, D, T, L):
	""" Takes a hostTree, parasiteTree, tip mapping function phi, and duplication cost (D), 
	transfer cost (T), and loss cost (L) and returns the DTL graph in the form of a dictionary, 
	with event scores set to 1. Cospeciation is assumed to cost 0. """
	DTL, numRecon = DP.DP(hostTree, parasiteTree, phi, D, T, L)
	newDTL = {}
	for vertex in DTL:
		newDTL[vertex] = []
		for i in range(len(DTL[vertex]) - 1):
			event = DTL[vertex][i]
			event = event[:-1] + [1.0]
			newDTL[vertex] = newDTL[vertex] + [event]
		newDTL[vertex] = newDTL[vertex] + [DTL[vertex][-1]]
	return newDTL


def branch(tree, treeOrder):
	"""Computes Ultra-metric Branchlength from a tree dating"""
	branches = {}
	for key in tree:
		if key != None:
			for child in tree[key]:
				if child != None:
					branches[child] = abs(treeOrder[child] - treeOrder[key])
	for key in treeOrder:
		if not key in branches:
			branches[key] = 0
	return branches

def findRoot(Tree):
    """This function takes in a parasiteTree and returns a string with the name of
    the root vertex of the tree"""

    if 'pTop' in Tree:
    	return Tree['pTop'][1]
    return Tree['hTop'][1]

def InitDicts(tree):
	"""This function takes as input a tree dictionary and returns a dictionary with all of the bottom nodes 
	of the edges as keys and empty lists as values."""
	treeDict = {}
	for key in tree:
		if key == 'pTop':
			treeDict[tree[key][1]] = [] 
		elif key == 'hTop':
			treeDict[tree[key][1]] = []
		else:
			treeDict[key[1]] = []
	return treeDict

def treeFormat(tree):
	"""Takes a tree in the format that it comes out of newickFormatReader and converts it into a dictionary
	with keys which are the bottom nodes of the edge and values which are the children."""
	treeDict = InitDicts(tree)
	treeRoot = findRoot(tree)
	for key in tree:
		if key == 'hTop' or key == 'pTop':
			if tree[key][-2] == None:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-2]]
			else:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-2][1]]
			if tree[key][-1] == None:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-1]]
			else:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-1][1]]
		else:
			if tree[key][-2] == None:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-2]]
			else:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-2][1]]
			if tree[key][-1] == None:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-1]]
			else:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-1][1]]
	return treeDict



def main():
	Reconcile(argv)

if __name__ == "__main__": main()