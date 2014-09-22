import os
import sys
import codecs
import re
import locale
from xml.sax.saxutils import escape

from Node import *;
from Helper import *;

import hashlib


class ChunkNode() :
    
    def __init__(self, header) :
        self.text = []
        self.header = header
        self.footer = None
        self.nodeList = []
        self.parent = '0'
        self.__attributes = {}
        self.parentRelation = 'root'
        self.name = None
        self.type = None
        self.head = None
        self.isParent = False
        self.errors = []
        self.upper = None
        self.updateDrel()
        self.type = None
        self.fsList = None
        self.phrase = ""

    def analyzeChunk(self)  :
        [chunkType,chunkFeatDict,chunkFSList] = getChunkFeats(self.header)
        self.fsList = chunkFSList
        self.type = chunkType
        self.updateAttributes(chunkFeatDict)
        self.text = '\n'.join([line for line in self.text])

        #Update chunk phrase
        for node in self.nodeList:
            if isinstance(node, ChunkNode):
                self.phrase += node.phrase.strip()+" "
            else:
                self.phrase += node.base64Lex.strip()+" "

        import hashlib
        self.id = hashlib.md5(self.phrase.encode('utf-8')).hexdigest()[:8]
    
    def updateAttributes(self,fsDict) :
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()
        self.updateDrel()

    def assignName(self) :
        if self.__attributes.has_key('name') : 
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this chunk Node')

    # Implemented by SPM, a recursive implementation which assigns the 
    # Hash of the lex as its name 
    def assignNames(self):
        self.__attributes['name'] = hashlib.md5(self.phrase).hexdigest()[:8]
        self.assignName()
        for node in self.nodeList:
            node.assignNames() #Propagate into the tree
        
    def updateDrel(self) :
        if self.__attributes.has_key('drel') :
            drelList = self.getAttribute('drel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('drel').split(':')[0]
        elif self.__attributes.has_key('dmrel') :
            drelList = self.getAttribute('dmrel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('dmrel').split(':')[0]

    def printValue(self) :
        returnString = []
        for node in self.nodeList :
            returnString.append(node.printValue())
        return ' '.join(x for x in returnString)

    def printSSFValue(self, prefix, allFeat) :
        returnStringList = []
        returnValue = [prefix , '((' , self.type]
        if allFeat == False : 
            fs = ['<fs']
            for key in self.__attributes.keys() :
                fs.append(key + "='" + self.getAttribute(key) + "'")
            delim = ' '
            fs[-1] = fs[-1] + '>'
            
        else :
            fs = self.fsList
            delim = '|'
        
        returnStringList.append('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))
        nodePosn = 0
        for node in self.nodeList :
            nodePosn += 1
            if isinstance(node,ChunkNode) :
                returnStringList.extend(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
            else :
                returnStringList.append(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
        returnStringList.append('\t' + '))')
        return returnStringList

    def getAttribute(self,key) :
        if self.__attributes.has_key(key) :
            return self.__attributes[key]
        else :
            return None

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]

    def getXML(self) :
        xml = '<chunkNode type="'+escape(str(self.type))+'" '
        xml += 'phrase="' + escape(self.phrase)+'" '
        #xml += 'id="' + escape(self.id)+'" '
        xml += 'id="' + escape(self.id)+'" '
        for attr in self.__attributes.keys():
            xml+= 'attr_'+escape(attr)+'="'+escape(self.__attributes[attr])+'" '
        xml += ">"
        for node in self.nodeList:
            xml += node.getXML()

        xml += "</chunkNode>"
        return xml



