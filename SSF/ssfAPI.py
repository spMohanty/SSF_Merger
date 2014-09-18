#!/usr/bin/env python
import os
import sys
import codecs
import re
import locale

from Node import *;
from ChunkNode import *;
from Document import *;
from Sentence import *;
from Helper import *;


sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 


if __name__ == '__main__' :
    
    inputPath = sys.argv[1]
    fileList = folderWalk(inputPath)
    print fileList
    newFileList = []
    for fileName in fileList :
        xFileName = fileName.split('/')[-1]
        if xFileName == 'err.txt' or xFileName.split('.')[-1] in ['comments','bak'] or xFileName[:4] == 'task' :
            continue
        else :
            newFileList.append(fileName)

    for fileName in newFileList :
        print fileName
        d = Document(fileName)
        def recurse(d):
            for k in d.nodeList:
                if k.__class__.__name__=="ChunkNode":
                    # print "="*10
                    # print k.getXML()
                    #print k.phrase
                    foo=1
                if k.__class__.__name__=="Sentence":
                    print "="*10
                    print k.getXML()
                if k.__class__.__name__=="Node":
                    # print k.printValue(), k.index
                    # print k.text
                    # print "="*20
                    # print k.text
                    # print k.getXML()
                    foo = 1
                else:
                    recurse(k)



        recurse(d)

        # for tree in d.nodeList : 
        #     for chunkNode in tree.nodeList :
        #         for node in chunkNode.nodeList :
        #             print node.printValue(), node.index
        #             # refAddress = node.getAttribute('ref')
        #             # if refAddress != None :
        #             #     refNode = getAddressNode(refAddress, node)
        #             #     print 'Anaphor' , node.printValue() , 'Reference' , refNode.printValue()
        #             #    print tree.printSSFValue()
        #             #    print tree.header + tree.text + tree.footer
    
