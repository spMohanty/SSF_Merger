import os
import sys
import codecs
import re
import locale
import hashlib

from Node import *;
from ChunkNode import *;
from Helper import *;


class Sentence() :
    def __init__(self, sentence, ignoreErrors = True, nesting = True, dummySentence = False) :
        self.ignoreErrors = ignoreErrors
        self.nesting = nesting
        self.sentence = None
        self.sentenceID = None
        self.sentenceType = None
        self.length = 0
        self.tree = None
        self.nodeList = []
        self.edges = {}
        self.nodes = {}
        self.tokenNodes = {}
        self.rootNode = None
        self.fileName = None
        self.comment = None
        self.probSent = False
        self.errors = []
        self.dummySentence = dummySentence
        if self.dummySentence == False :
            
            self.header = sentence.group('header')
            self.footer = sentence.group('footer')
            self.name = sentence.group('sentenceID')
            self.text = sentence.group('text')
            self.analyzeSentence()

    def analyzeSentence(self, ignoreErrors = False, nesting = True) :        

        contextList = [self]
        nodeIndex = 0  
        for line in self.text.split('\n') :
            stripLine = line.strip()
            
            if stripLine=="" :
                continue
            elif stripLine[0]=="<" and ignoreErrors == False :            
                    self.errors.append('Encountered a line starting with "<"')
                    self.probSent = True
            else :
                splitLine = stripLine.split()
                
                #Chunk Starts
                if len(splitLine)>1 and splitLine[1] == '((' :
                    currentChunkNode = ChunkNode(line + '\n')
                    currentChunkNode.upper = contextList[-1]
                    currentChunkNode.upper.nodeList.append(currentChunkNode)

                    if currentChunkNode.upper.__class__.__name__ != 'Sentence' :
                        currentChunkNode.upper.text.append(line)

                    contextList.append(currentChunkNode)

                elif len(splitLine)>0 and splitLine[0] == '))' :
                    
                    currentChunkNode.footer = line + '\n'
                    currentChunkNode.analyzeChunk()
                    contextList.pop(-1)

                    if not isinstance(contextList[-1], Sentence):
                        currentChunkNode = contextList[-1] 
                else :
                    currentNode = Node(line + '\n', str(self.name)+"_"+str(nodeIndex))
                    nodeIndex += 1
                    currentNode.upper = contextList[-1]
                    contextList[-1].nodeList.append(currentNode)
    
        # updateAttributesStatus = self.updateAttributes()
        # if updateAttributesStatus == 0 :
        #     self.probsent = True
        #     self.errors.append("Cannot update the Attributes for this sentence")
        
    def addEdge(self, parent , child) :
        if parent in self.edges.iterkeys() :
            if child not in self.edges[parent] : 
                self.edges[parent].append(child)
        else :
            self.edges[parent] = [child]

    def updateAttributes(self) :
        populateNodesStatus = self.populateNodes()
        populateEdgesStatus = self.populateEdges()
        self.sentence = self.generateSentence()
        if populateEdgesStatus == 0 or populateNodesStatus == 0:
            return 0
        return 1

    def printSSFValue(self, allFeat = True) :
        returnStringList = []
        returnStringList.append("<Sentence id='" + str(self.name) + "'>")
        if self.nodeList != [] :
            nodeList = self.nodeList
            nodePosn = 0
            for node in nodeList :
                nodePosn += 1
                returnStringList.extend(node.printSSFValue(str(nodePosn), allFeat))
        returnStringList.append( '</Sentence>\n')
        return '\n'.join(x for x in returnStringList)
        
    def populateNodes(self , naming = 'strict') :
        if naming == 'strict' : 
            for nodeElement in self.nodeList :
                assert nodeElement.name is not None
                self.nodes[nodeElement.name] = nodeElement
        return 1
    
    def populateEdges(self) :
        for node in self.nodeList :
            nodeName = node.name
            if node.parent == '0'  or node == self.rootNode:
                self.rootNode = node
                continue
            elif node.parent not in self.nodes.iterkeys() :
#                self.errors.append('Error : Bad DepRel Parent Name ' + self.fileName + ' : ' + str(self.name))
                return 0
            assert node.parent in self.nodes.iterkeys()
            self.addEdge(node.parent , node.name)
        return 1

    def generateSentence(self) :
        sentence = []
        for nodeName in self.nodeList :
            sentence.append(nodeName.printValue())
        return ' '.join(x for x in sentence)

    def assignNames(self):
        for node in self.nodeList:
            node.assignNames()

    def getXML(self):
        xml = '<Sentence id="'+escape(str(self.name))+'">'
        for node in self.nodeList:
            xml+= node.getXML()

        xml += "</Sentence>\n"
        return xml
