def assignNodeNames(nodeList) :
    nameDict = {}
    for node in nodeList :
        count = nameDict.setdefault(node.type , 1)
        if count !=1 :
            node.addAttribute('name', node.type + str(count))
        else :
            node.addAttribute('name', node.type)
        node.assignName()
        nameDict[node.type] += 1

def assignTokenNodeNames(nodeList) :
    nameDict = {}
    for node in nodeList :
        count = nameDict.setdefault(node.lex , 1)
        if count !=1 :
            node.addAttribute('name', node.lex + str(count))
        else :
            node.addAttribute('name', node.lex)
        node.assignName()
        nameDict[node.lex] += 1

