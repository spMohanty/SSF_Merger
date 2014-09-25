import os
import sys
import codecs
import re
import locale
import hashlib
import base64

from Helper import *;
from xml.sax.saxutils import escape


class Node() :
    def __init__(self,text, nodeIndex = None) :
        self.index = nodeIndex
        self.text = text
        self.lex = None
        self.base64Lex = None #Helpful when you want to use lex as an attribute value in a XML like scheme and " or ' can also be values
        self.type = None
        self.__attributes = {}
        self.errors = []
        self.name = None
        self.parent = None
        self.parentRelation = None
        self.alignedTo = None
        self.fsList = None
        self.analyzeNode(self.text)

    def analyzeNode(self, text) :
        [token, tokenType, fsDict, fsList] = getTokenFeats(text.strip().split())
        attributeUpdateStatus = self.updateAttributes(token, tokenType, fsDict, fsList)
        if attributeUpdateStatus == 0 :
            self.errors.append("Can't update attributes for node")
            self.probSent = True

    
    def updateAttributes(self,token, tokenType, fsDict, fsList) :
        self.fsList = fsList
        self.lex = token
        self.base64Lex = base64.b64encode(self.lex.encode('utf8'))
        self.type = tokenType
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()

    def assignName(self) :
        if self.__attributes.has_key('name') : 
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this token Node')

    def assignNames(self):
        #Implemented by SPM, uses the index as a name for the node
        self.__attributes['name'] = str(self.index)
        self.assignName()
            
    def printValue(self) :
        return self.lex

    def printSSFValue(self, prefix, allFeat) :
        returnValue = [prefix , self.printValue() , self.type]
        if allFeat == False : 
            fs = ['<fs']
            for key in self.__attributes.keys() :
                fs.append(key + "='" + self.getAttribute(key) + "'")
            delim = ' '
            fs[-1] = fs[-1] + '>'
            
        else :
            fs = self.fsList
            delim = '|'
        return ('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))

    def getAttribute(self,key) :
        if self.__attributes.has_key(key) :
            return self.__attributes[key]
        else :
            return None
    def getAttributeList(self):
        return self.__attributes.keys()

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]

    # Returns a XML representation of the current Node
    # Will be useful when trying to use external libraries for 
    # Tree operations
    def getXML(self):
        xml = ''
        xml += '<node '
        xml += 'id="'+escape(self.index) + '" '
        xml += 'lex="' + escape(self.base64Lex) + '" '
        xml += 'type="' + escape(self.type) + '" '
        for attr in self.getAttributeList():
            xml+= 'attr_'+escape(attr)+'="'+escape(self.getAttribute(attr))+'" '
        xml += "/>"

        return xml