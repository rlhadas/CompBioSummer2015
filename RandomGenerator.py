# RandomGenerator.py
# Annalise Schweickart, July 2015


import random
import newickFormatReader
import orderGraph
import DP
import reconciliationGraph
import os

def findRoot(Tree):
    """This function takes in a Tree and returns a string with the name of
    the root vertex of the tree"""

    if 'pTop' in Tree:
        return Tree['pTop'][1]
    return Tree['hTop'][1] 


def orderDTL(DTL, ParasiteRoot):
    """This function takes in a DTL graph and the ParasiteRoot. It outputs a
    list, keysL, that contains tuples. Each tuple has two elements. The first
    is a mapping node of the form (p, h), where p is a parasite node and h is
    a host node. The second element is a level representing the depth of that
    mapping node within the tree."""

    keysL = []
    topNodes = []
    for key in DTL:
        if key[0] == ParasiteRoot:
            topNodes.append(key)
    for vertex in topNodes:
        keysL.extend(orderDTLRoots(DTL, vertex, 0))
    return keysL

def orderDTLRoots(DTL, vertex, level):
    """this function takes a DTL graph, one node, vertex, of the DTL graph, 
    and a level, and returns a list, keysL, that contains tuples. Each tuple
    has two elements. The first is a mapping node of the form (p, h), where p
    is a parasite node and h is a host node. The second element is a level 
    representing the depth of that mapping node within the tree. This function
    adds the input vertex to keysL and recurses on its children."""

    keysL = []
    for i in range(len(DTL[vertex]) - 1):    # loop through each event of key
        event = DTL[vertex][i]
        child1 = event[1]
        child2 = event[2]
        keysL = keysL + [(vertex, level)]
        if child1[0] != None:
            keysL.extend(orderDTLRoots(DTL, child1, level + 1))
        if child2[0] != None:
            keysL.extend(orderDTLRoots(DTL, child2, level + 1)) 
    return keysL


def sortHelper(DTL, keysL):
    """This function takes in a list orderedKeysL and deals with duplicate 
    mapping nodes that could potentially have the same level or have two 
    different levels, in which case we want to choose the highest level 
    because we are using the bottom-up approach"""
    
    uniqueKeysL = []
    for key in DTL:
        maxLevel = float("-inf")
        for element in keysL:
            if key == element[0]:
                if element[1] > maxLevel:
                    maxLevel = element[1]
        uniqueKeysL.append((key, maxLevel))
    return uniqueKeysL


def preorderDTLsort(DTL, ParasiteRoot):
    """This takes in a DTL dictionary and parasite root and returns a sorted
    list, orderedKeysL, that is ordered by level from smallest to largest,
    where level 0 is the root and the highest level has tips."""

    keysL = orderDTL(DTL, ParasiteRoot)
    uniqueKeysL = sortHelper(DTL, keysL)
    orderedKeysL = []
    levelCounter = 0
    while len(orderedKeysL) < len(uniqueKeysL):
        for mapping in uniqueKeysL:
            if mapping[-1] == levelCounter:
                orderedKeysL = orderedKeysL + [mapping]
        levelCounter += 1
    return orderedKeysL

def normalizer(DTL):
    """Takes in a DTL graph and normalizes the scores within a key,
    returning a new DTL with normalized scores"""
    for key in DTL.keys():
        totalScore = 0
        for event in DTL[key][:-1]:
            totalScore += event[-1]
        for event in DTL[key][:-1]:
            event[-1] = event[-1]/totalScore
    return DTL

def normalizeList(scoreList):
    """Takes in a list of scores and returns a new list with those scores
    normalized"""
    totalScore = 0
    newScoreList = []
    for score in scoreList:
        totalScore+=score
    for score in scoreList:
        newScoreList.append(score/totalScore)
    return newScoreList

def rootGenerator(DTL, parasiteTree):
    """Generates a list of the roots in a DTL graph"""
    parasiteRoot = findRoot(parasiteTree)
    preOrder = preorderDTLsort(DTL, parasiteRoot)
    rootList = []
    for key in preOrder:
        if key[1] == 0:
            rootList.append(key[0])
    return rootList

def biasedChoice(rootList, probList):
    """Takes in a list of vertex pairs and a correspondiing list of their 
    frequencies and returns a vertex pair randomly chosen but weighted by
    its frequency"""
    scoreSum = 0
    rangeList = []
    for n in range(len(rootList)):
        rangeList.append((scoreSum, scoreSum+probList[n], rootList[n]))
        scoreSum += probList[n]
    choice = random.random()
    for n in rangeList:
        if n[0]<=choice<n[1]:
            return n[2]


def makeProbList(DTL, root):
    """Takes as input a DTL graph and a root and returns the frequencies 
    associated with the events occuring at that root in a list"""
    probList = []
    for event in DTL[root][:-1]:
        probList.append(event[-1])
    return probList


def uniformRecon(DTL, rootList, randomRecon):
    '''Takes as input a DTL graph, a rootList, and a growing reconciliation
    dictionary and recursively builds the reconciliation dictionary, choosing
    random events'''
    if rootList ==[]:
        return randomRecon  
    newRootL = []   
    for root in rootList:
        newChild = random.choice(DTL[root][:-1])
        randomRecon[root] = newChild
        if newChild[1] != (None, None) and not newChild[1] in randomRecon and\
        not newChild[1] in newRootL:
            newRootL.append(newChild[1])
        if newChild[2] != (None, None) and not newChild[2] in randomRecon and\
        not newChild[2] in newRootL:
            newRootL.append(newChild[2])
    return uniformRecon(DTL, newRootL, randomRecon)


def biasedRecon(DTL, rootList, randomRecon):
    '''Takes in a DTL graph, a list of vertex pairs, and a dictionary of the
    growing reconciliation and recursively builds the reconciliation using 
    biasedChoice to decide which events will occur'''
    if rootList ==[]:
        return randomRecon  
    newRootL = []   
    for root in rootList:
        print root
        probList = makeProbList(DTL, root)
        newChild = biasedChoice(DTL[root][:-1],probList)
        print "newChild",newChild
        randomRecon[root] = newChild
        if newChild[1] != (None, None) and not newChild[1] in randomRecon and\
        not newChild[1] in newRootL:
            newRootL.append(newChild[1])
        if newChild[2] != (None, None) and not newChild[2] in randomRecon and\
        not newChild[2] in newRootL:
            newRootL.append(newChild[2])
    return biasedRecon(DTL, newRootL, randomRecon)


def randomReconWrapper(dirName, D, T, L, numSamples, typeGen):
    """Takes in a file and duplication, loss and transfer costs, and calls 
    randomReconGen to build a random reconciliation"""
    f = open('results.txt', 'w')
    f.write(typeGen+" random reconciliations"+"/n")
    totalTimeTravel = 0
    outOf = 0
    for fileName in os.listdir("TreeLifeData"):
        if fileName.endswith('.newick'):
            outOf += numSamples
            hostTree, parasiteTree, phi = newickFormatReader.getInput("TreeLifeData/"+fileName)
            DTL, numRecon = DP.DP(hostTree, parasiteTree, phi, D, T, L)
            rootList = rootGenerator(DTL, parasiteTree)
            randomReconList = []
            for n in range(numSamples):
                timeTravelCount = 0
                startRoot = random.choice(rootList)
                if typeGen == "uniform":
                    currentRecon = uniformRecon(DTL, [startRoot], {})
                else: 
                    normalizeDTL = normalizer(DTL)
                    currentRecon = biasedRecon(normalizeDTL, [startRoot], {})
                for key in currentRecon.keys():
                    currentRecon[key] = currentRecon[key][:-1]
                randomReconList.append(currentRecon)
                graph = reconciliationGraph.buildReconstruction\
                    (hostTree, parasiteTree, randomReconList[n])
                currentOrder = orderGraph.date(graph)
                if currentOrder == 'timeTravel':
                    timeTravelCount += 1
                    totalTimeTravel += 1
            f.write(fileName+" contains "+str(timeTravelCount)+" temporal "+ \
                "inconsistencies out of "+ str(len(randomReconList))+ \
                " reconciliations."+"\n")
    f.close()
    print "Total fraction of temporal inconsistencies: ", totalTimeTravel, '/', outOf









