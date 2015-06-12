

#Team Srinidhi and Juliet

#Our goal is to find the k best reconciliations

def findRoot(ParasiteTree):
    """This function takes in a parasiteTree and returns a string with the name of
    the root vertex of the tree"""
    ParasiteRoot = ParasiteTree['pTop'][1]
    return ParasiteRoot


def orderDTLwrapper(DTL, ParasiteRoot):
    """This wrapper function uses orderDTL and starts with a level of 0. Returns keysL."""
    return orderDTL(DTL, ParasiteRoot, 0)

def orderDTL(DTL, ParasiteRoot, level):
    """This function takes in a DTL dictionary, a ParasiteRoot, and a level that represents the depth of 
    the of a vertex pair. It returns a list, keysL, that includes tuples with the first 
    elements being a mapping node of the form (p, h), and the second element being the depth of that node within 
    the graph. This function loops through the DTL graph and recruses on the two children of each DTL 
    mapping node, adding the results to keysL"""

    keysL = []
    for key in DTL:
        if key[0] == ParasiteRoot:
            for i in range(len(DTL[key]) - 1):          #loop through each event associated with key in DTL
                event = DTL[key][i]
                child1 = event[1]
                child2 = event[2]
                if child1[0] == None and child2[0] == None:    #base case: mapping node (key) is a tip
                    keysL = keysL + [(key, level)]
                elif child2[0] == None:                        #loss case: there is only one child (child1)
                    keysL = keysL + [(key, level)] + orderDTL(DTL, child1[0], level + 1)
                elif child1[0] == None:                        #loss case: there is only one child (child2)
                    keysL = keysL + [(key, level)] + orderDTL(DTL, child2[0], level + 1)
                else:
                    keysL = keysL + [(key, level)] + orderDTL(DTL, child1[0], level + 1) + orderDTL(DTL, child2[0], level + 1)
    return keysL


def postorderDTLsort(DTL, ParasiteRoot):
    """This takes in a DTL dictionary and parasite root and returns a sorted list, orderedKeysL, that is ordered
    by level from largest to smallest, where level 0 is the root and the highest level has tips."""
    #keysL = [(('p6', 'h6'), 0), (('p1', 'h1'), 1), (('p8', 'h8'), 1), (('p2', 'h2'), 2), (('p3', 'h3'), 2)]
    keysL = orderDTLwrapper(DTL, ParasiteRoot)
    orderedKeysL = []
    levelCounter = 0
    while len(orderedKeysL) < len(keysL):
        for mapping in keysL:
            if mapping[-1] == levelCounter:
                orderedKeysL = [mapping] + orderedKeysL
        levelCounter += 1
    return orderedKeysL

def preorderDTLsort(DTL, ParasiteRoot):
    """This takes in a DTL dictionary and a parasite root and returns a sorted list, orderedKeysL, that is ordered
    by level from smalles to largest, where level 0 is the root and the highest level has tips."""
    keysL = orderDTLwrapper(DTL, ParasiteRoot)
    orderedKeysL = []
    levelCounter = 0
    while len(orderedKeysL) < len(keysL):
        for mapping in keysL:
            if mapping[-1] == levelCounter:
                orderedKeysL = orderedKeysL + [mapping] 
        levelCounter += 1
    return orderedKeysL


     

def bookkeeping(DTL, ParasiteTree):
    """This function inputs the DTL graph and ParasiteTree, and then records what the max is at each mapping node and 
    where the max came from. It outputs two dictionaries BSFHMap and BSFHEvent, by looping through the keys in orderedKeysL 
    and finding the max score at each mapping node and event node"""

    """We are creating two dictionaries. BSFHMap has keys of the form (p, h) which are the mapping nodes, and values
    which are lists where the first element is a list of events with the max score, and the last element is the max score.
    BSFHEvent is a dictionary with events as keys, and values which are one number which is the max score."""

    #BSFHMap = {(mapping node): [['event', (p, h), (p, h), score], maxScore]}
    #BSFHEvent = {(event node): max}

    TIPSCORE = 1 #this will change depending on how we define the score for tips

    BSFHMap = {}
    BSFHEvent = {}


    ParasiteRoot = findRoot(ParasiteTree)   

    orderedKeysL = postorderDTLsort(DTL, ParasiteRoot)

    for key in orderedKeysL:
        mapNode = key[0]

        if DTL[mapNode][0][0] == 'C':                   #check if the key is a tip
           BSFHMap[mapNode] = [DTL[mapNode][0], TIPSCORE]    #set BSFH of tip to some global variable

        else:                                       #if key isn't a tip:
            maxScore = 0                             #initialize counter
            maxEvent = []                           #initialize variable to keep track of where max came from

            for i in range(len(DTL[mapNode]) - 1):   #iterate through the events associated with the key node
                event = tuple(DTL[mapNode][i])
                BSFHEvent[event] = BSFHMap[event[1]][-1] + BSFHMap[event[2]][-1]

                if BSFHEvent[event] > maxScore:  #check if current event has a higher score than current max
                    maxScore = BSFHEvent[event]  #if so, set new max score
                    maxEvent = event                #record where new max came from

                elif BSFHEvent[event] == maxScore: # if event score ties with another event, add both to the dictionary
                    maxEvent.append(event)

            BSFHMap[mapNode] = [maxEvent, maxScore]      #set BSFH value of key

    return BSFHMap


def TraceChildren(GreedyOnce, BSFHMap, key):
    """This function takes a dicitonary of a best reconciliation, a BSFHMap dicitonary, and a current key, and adds the 
    children of that key to the dictionary, then recurses on the children."""
    child1 = GreedyOnce[key][1]
    child2 = GreedyOnce[key][2]
    if child1 != (None, None):
        GreedyOnce[child1] = BSFHMap[child1][0][0:3]
        GreedyOnce.update(TraceChildren(GreedyOnce, BSFHMap, child1))
    if child2 != (None, None):
        GreedyOnce[child2] = BSFHMap[child2][0][0:3]
        GreedyOnce.update(TraceChildren(GreedyOnce, BSFHMap, child2))
    return GreedyOnce


def greedyOnce(DTL, ParasiteTree):
    """This function takes DTL, ParasiteTree, as inputs and calls bookkeeping to find BSFHMap, which is a dictionary. 
    It returns the reconciliation tree with the highest score in a dictionary called GreedyOnce, and also resets to 0 the scores 
    of the mapping nodes in the best reconciliation. The return dictionary will have keys which are the mapping nodes in the best 
    reconciliation, and values of the form (event, child1, child2)."""


    BSFHMap = bookkeeping(DTL, ParasiteTree)
    ParasiteRoot = findRoot(ParasiteTree)

    GreedyOnce = {}                     #initialize dictionary we will return

    bestKey = ()                        #variable to hold the key with the highers BSFH value
    bestScore = 0                       #variable to hold the highest BSFH value seen so far
    for key in BSFHMap:                                             #iterate trough all the keys (verteces) in BSFHMap
        if BSFHMap[key][-1] > bestScore and key[0] == ParasiteRoot: #check if key has a score higher than bestScore and includes ParasiteRoot
            bestKey = key
            bestScore = BSFHMap[key][-1]
    GreedyOnce[bestKey] = BSFHMap[bestKey][0][0:3]                  #set value in GreedyOnce of the best key we found
    GreedyOnce.update(TraceChildren(GreedyOnce, BSFHMap, bestKey))
    return GreedyOnce


            





def Greedy(things):
    """Greedy is also going to reset the BSFH scores to 0 and then call bookkeeping with the new DTL. We do this k times"""
























