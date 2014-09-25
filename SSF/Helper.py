import os
import sys
import codecs
import re
import locale

import lxml
import base64


def getAddressNode(address, node, level = 'ChunkNode') :
    
    ''' Returns the node referenced in the address string relative to the node in the second argument.
        There are levels for setting the starting address-base. These are "ChunkNode", "Node" , "Sentence" , "Document" , "Relative".
        The hierarchy of levels for interpretation is :
        "Document" -> "Sentence" -> "ChunkNode" -> "Node"
        "Relative" value starts the base address from the node which contains the address. This is also the default option.
    '''

    currentContext = node

    if level != 'Relative' : 
        while(currentContext.__class__.__name__ != level) :
            currentContext = currentContext.upper
            
    currentContext = currentContext.upper
    
    stepList = address.split('%')
    
    for step in stepList :
        if step == '..' :
            currentContext = currentContext.upper
        else :
            refNode = [iterNode for iterNode in currentContext.nodeList if iterNode.name == step][0]
            currentContext = refNode
    return refNode

def getChunkFeats(line) :
    lineList = line.strip().split()
    chunkType = None
    fsList = []
    if len(lineList) >= 3 : 
        chunkType = lineList[2]
        
    returnFeats = {}
    multipleFeatRE = r'<fs.*?>'
    featRE = r'(?:\W*)(\S+)=([\'|\"])?([^ \t\n\r\f\v\'\"]*)[\'|\"]?(?:.*)'
    fsList = re.findall(multipleFeatRE, ' '.join(lineList))
    for x in lineList :
        feat = re.findall(featRE, x)
        if feat!=[] :
            if len(feat) > 1 :
                returnErrors.append('Feature with more than one value')
                continue
            returnFeats[feat[0][0]] = feat[0][2]

    return [chunkType,returnFeats,fsList]

def getTokenFeats(lineList) :
    tokenType, token = None , None
    returnFeats = {}
    fsList = []
    if len(lineList) >=3 :
        tokenType = lineList[2]

    token = lineList[1]
    multipleFeatRE = r'<fs.*?>'
    featRE = r'(?:\W*)(\S+)=([\'|\"])?([^ \t\n\r\f\v\'\"]*)[\'|\"]?(?:.*)'
    fsList = re.findall(multipleFeatRE, ' '.join(lineList))
    for x in lineList :
        feat = re.findall(featRE, x)
        if feat!=[] :
            if len(feat) > 1 :
                returnErrors.append('Feature with more than one value')
                continue
            returnFeats[feat[0][0]] = feat[0][2]

    return [token,tokenType,returnFeats,fsList]
        
def getSentenceIter(inpFD) :

    sentenceRE = r'''(?P<complete>(?P<header><Sentence id=[\'\"]?(?P<sentenceID>\d+)[\'\"]?>)(?P<text>.*?)(?P<footer></Sentence>))'''
    text = inpFD.read()    
    # print text
    return re.finditer(sentenceRE, text, re.DOTALL)

def folderWalk(folderPath):
    import os
    fileList = []
    for dirPath , dirNames , fileNames in os.walk(folderPath) :
        for fileName in fileNames : 
            fileList.append(os.path.join(dirPath , fileName))
    return fileList

#Only supports from Sentence level from now
import re
def get_fs_line(tree):
    output = "<fs "
    count = 0
    if "attr_af" in tree.attrib.keys():
        output+="af='"+tree.attrib["attr_af"]+"' "
        count+=1
    for attr in tree.attrib.keys():
        if attr!="attr_af" and re.match("attr_.*", attr):
            output += attr.replace("attr_","")+'="'+tree.attrib[attr]+'" '
            count += 1

    output += " >"

    if count == 0:
        return ""
    else:
        return output


indexList = []
def XML_TO_SSF(tree, depth=0 ):
    if depth==0:
        ##Sentence Level
        global indexList
        indexList = []

    ##Pre recurse
    output = ""
    if tree.tag == "Sentence":
        output = "<Sentence id='"+tree.attrib['id']+"'>\n"
    elif tree.tag == "chunkNode":
        output = ".".join([str(x) for x in indexList])
        output += "\t" + "((\t" + tree.attrib['type'] + "\t"
        output += get_fs_line(tree) + "\n"

    elif tree.tag=="node":
        output = ".".join([str(x) for x in indexList])
        output += "\t" + base64.b64decode(tree.attrib['lex']).decode('utf8').encode('ascii', 'backslashreplace') +"\t"+tree.attrib['type']+"\t"
        output += get_fs_line(tree) + "\n"

    ##Recurse

    index = 1
    for child in tree.getchildren():
        indexList.append(index)
        output+=XML_TO_SSF(child, depth+1)
        indexList.pop(-1)
        index+=1

    ##Post recurse
    if tree.tag == "Sentence":
        output += "</Sentence>\n"
    elif tree.tag == "chunkNode":
        output += "\t" + "))\n"

    elif tree.tag=="node":
        ##No such case. Only adding for consistency
        output += ""
    return output

