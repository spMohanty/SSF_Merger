import os
import sys
import codecs
import re
import locale

from Node import *;
from ChunkNode import *;
from Sentence import *;
from Helper import *;
import Helper

class Document() :

    def __init__(self, fileName) :
        self.header = None
        self.footer = None
        self.text = None
        self.nodeList = []
        self.fileName = fileName
        self.analyzeDocument()
        self.upper = None
        
    def analyzeDocument(self) :
        inputFD = codecs.open(self.fileName, 'r', encoding='utf8')
        sentenceList = Helper.getSentenceIter(inputFD)
        for sentence in sentenceList :
            tree = Sentence(sentence, ignoreErrors = True, nesting = True)
            tree.upper = self
            self.nodeList.append(tree)
        inputFD.close()