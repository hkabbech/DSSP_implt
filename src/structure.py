"""@package structure

Secondary structures assignment
4-helices (H) -> isolated beta-bridge (B) -> beta-strands (E) -> 3-helices (G)
-> 5-helices (I) -> n-turns (T) -> bends (S)
"""

############################## V A R I A B L E S ###############################
NONE = ' '

# n-turn patterns:
START = '>'
END = '<'
START_END = 'X'
MIDDLE = { 3: '3', 4: '4', 5: '5' }

# Secondary structural patterns :
HELIX = { 3: 'G', 4: 'H', 5: 'I' }
STRAND = 'E'
TURN = 'T'
BRIDGE = 'B'
BEND = 'S'

# Alphabet :
ABC_LOWER, ABC_UPPER = [], []
for letter in range(65,91):
    ABC_UPPER.append(chr(letter))
    ABC_LOWER.append(chr(letter+32))

################################ H - B O N D S #################################

def isHbond(ri,rj):
    """Test if there is an H-bond between residue i and j. Return a boolean."""
    # Fixed variables :
    Q1, Q2 = 0.41, 0.20 # partial charges
    F = 332 # factor
    try:
        # dAB = Interatomic distance from atom A (residue i) to B (residue j)
        dON = rj.N - ri.O
        dCH = rj.H - ri.C
        dOH = rj.H - ri.O
        dCN = rj.N - ri.C

        # Electrostatic interaction energy between two H-bonding groups.
        # E in kcal/mol
        E = Q1 * Q2 * (1/dON + 1/dCH - 1/dOH - 1/dCN) * F
        if (E < -0.5):
            return(True)
        return(False)
    except:
        return(False)

######################## N T U R N S  &  H E L I C E S #########################

def isHelix(resList,i,n):
    """Test if residue i forms an n-helice with residue i+1. Return a boolean."""
    try:
        if (isHbond(resList[i],resList[i+n]) == True and isHbond(resList[i+1],resList[i+1+n]) == True):
            return(True)
        return(False)
    except:
        return(False)

def setNturnPatternResult(resList,res,n):
    if (resList[res].nturns[n].end == END):
        if (resList[res].nturns[n].start == START):
            # '>' + '[3,4,5]' + '<' = 'X' (start & end)
            resList[res].nturns[n].result = START_END
        else:
            # ' ' + '<' = '<' (end)
            resList[res].nturns[n].result = END
    else:
        if (resList[res].nturns[n].start == START):
            # '>' + ' ' = '>' (start)
            resList[res].nturns[n].result = START
        else:
            if (resList[res].nturns[n].middle != NONE):
                # (' ' + ' ') and (middle != ' ') =  [3,4,5] (middle)
                resList[res].nturns[n].result = MIDDLE[n]
    return(resList)

def setHelixStruct(resList,n):
    """ """
    for res in range(len(resList)):
        if (resList[res].structure != NONE): continue
        if (resList[res].nturns[n].result == START):
            while (resList[res+2].nturns[n].result != NONE):
                res += 1
                if (resList[res].structure == NONE):
                    resList[res].structure = HELIX[n]
    return(resList)

def setNturnsStruct(resList):
    """ """
    for n in [5,4,3]:
        for res in range(len(resList)):
            if (resList[res].nturns[n].result == START):
                while (resList[res+1].structure != NONE): res += 1
                while (resList[res+2].nturns[n].result != NONE):
                    res += 1
                    if (resList[res].structure == NONE):
                        resList[res].structure = TURN
    return(resList)

def foundHelices(resList,n):
    """Found all the n-helices and put the structure element"""
    for res in range(0,len(resList)):
        if (resList[res].structure != NONE): continue
        if (isHelix(resList,res,n)):
            for i in range(0,2):
                # helix start : res(i):'>' & res(i+1):'>'
                resList[res+i].nturns[n].start = START
                # helix end : res(i+n):'<' & res(i+n+1):'<'
                resList[res+n+i].nturns[n].end =  END
            for i in range(2,n):
                # helix middle : res(i+2):'[3,4,5]' & res(i+3):'[4,5]' & res(i+4):'[5]'
                resList[res+i].nturns[n].middle =  MIDDLE[n]
        setNturnPatternResult(resList,res,n)

    setHelixStruct(resList,n)
    return(resList)

def foundNturns(resList):
    for res in range(len(resList)-5):
        for n in [3,4,5]:
            if (isHbond(resList[res],resList[res+n]) == True):
                resList[res].nturns[n].start = START
                resList[res+n].nturns[n].end =  END
                for i in range(1,n):
                    resList[res+i].nturns[n].middle =  MIDDLE[n]
    for res in range(len(resList)):
        for n in [3,4,5]:
            setNturnPatternResult(resList,res,n)
    setNturnsStruct(resList)
    return(resList)

###################### B R I D G E S  &  S T R A N D S #########################

def isParallelBridge(resList,i,j):
    """Test if residues i and j form a parallel bridge. Return a boolean."""
    try:
        if ((isHbond(resList[i-1],resList[j]) == True and isHbond(resList[j],resList[i+1]) == True)\
        or (isHbond(resList[j-1],resList[i]) == True and isHbond(resList[i],resList[j+1]) == True)):
            return(True)
        return(False)
    except:
        return(False)

def isAntiparallelBridge(resList,i,j):
    """Test if residues i and j form an antiparallel bridge. Return a boolean."""
    try:
        if ((isHbond(resList[i],resList[j]) == True and isHbond(resList[j],resList[i]) == True)\
        or (isHbond(resList[i-1],resList[j+1]) == True and isHbond(resList[j-1],resList[i+1]) == True)):
            return(True)
        return(False)
    except:
        return(False)

def setIsolatedBridgeAndStrandStruct(resList):
    """   """
    for res in range(1,len(resList)-1):
        if (resList[res].structure != NONE): continue
        if ((resList[res].bp1+resList[res].bp2) != 0):
            # Isolated Beta-bridge :
            if (resList[res-1].bp1+resList[res-1].bp2 == 0 and resList[res+1].bp1+resList[res+1].bp2 == 0):
                resList[res].structure = BRIDGE
                resList[resList[res].bp1-1].structure = BRIDGE
            # Extanded strand :
            elif (resList[res-1].bp1+resList[res-1].bp2 != 0 or resList[res+1].bp1+resList[res+1].bp2 != 0):
                resList[res].structure = STRAND
        else:
            # Surrounded by strands :
            if (resList[res-1].bp1+resList[res-1].bp2 != 0 and resList[res+1].bp1+resList[res+1].bp2 != 0\
                and resList[res-2].bp1+resList[res-2].bp2 != 0 and resList[res+2].bp1+resList[res+2].bp2 != 0):
                resList[res].structure = STRAND
    return(resList)

def foundStrands(resList):
    """ """
    n = -1
    newStrand = True
    for res_i in range(len(resList)):
        if (resList[res_i].structure != NONE): continue
        for res_j in range(res_i+2,len(resList)):
            if (resList[res_j].structure != NONE): continue
            if (isParallelBridge(resList,res_i,res_j) == True or isAntiparallelBridge(resList,res_i,res_j) == True):
                if (isParallelBridge(resList,res_i,res_j) == True):
                    alphabet = ABC_LOWER
                    if (resList[res_i-1].bp1 == 0 or resList[res_i-1].bp1+1 != res_j+1):
                        newStrand = True
                    else:
                        newStrand = False
                elif (isAntiparallelBridge(resList,res_i,res_j) == True):
                    alphabet = ABC_UPPER
                    if (resList[res_i-1].bp1 == 0 or resList[res_i-1].bp1-1 != res_j+1):
                        newStrand = True
                    else:
                        newStrand = False
                if (resList[res_i+1].bp1 == 0 and resList[res_i-1].bp2 == 0):
                    if (newStrand == True):
                        n += 1
                        if (n == 26): n = 0
                    resList[res_i].bp1 = res_j+1
                    resList[res_i].bridge_1 = alphabet[n]
                else:
                    resList[res_i].bp2 = res_j+1
                    if (resList[res_i-1].bp2 == 0 and resList[res_i-2].bp2 == 0): # New strand
                        n += 1
                        if (n == 26): n = 0
                    resList[res_i].bridge_2 = alphabet[n]
                resList[res_j].bp1 = res_i+1
                resList[res_j].bridge_1 = alphabet[n]
    resList=setIsolatedBridgeAndStrandStruct(resList)
    return(resList)

################################## B E N D S ###################################

def setBendStruct(resList):
    """ """
    for res in range(len(resList)):
        if (resList[res].structure != NONE): continue
        if (resList[res].bend != NONE):
            resList[res].structure = BEND
    return(resList)

######## S E C O N D A R Y   S T R U C T U R E S    A S S I G N M E N T ########


def setSSE(resList):
    """Assignment of secondary structure elements in this order :
    4-helices (H) -> isolated beta-bridge (B) -> beta-strands (E) -> 3-helices (G)
    -> 5-helices (I) -> n-turns (T) -> bends (S)"""
    foundHelices(resList,4) # alpha-helices
    foundStrands(resList)
    foundHelices(resList,3) # 3_10-helices
    foundHelices(resList,5) # pi-helices
    foundNturns(resList)
    setBendStruct(resList)
    return(resList)
