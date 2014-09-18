#!/usr/bin/env python

import SSF
import sys
from copy import deepcopy

d1 = SSF.Document(sys.argv[1])
d2 = SSF.Document(sys.argv[2])

# Necessary because SSF -> XML is only supported for 
# Sentence level now
def getXMLofFirstSentence(d):
	for node in d.nodeList:
		if isinstance(node,SSF.Sentence):
			return node.getXML()
			break
		if not isinstance(node,SSF.Node):
			getXMLofFirstSentence(node)


XML1 = getXMLofFirstSentence(d1)
XML2 = getXMLofFirstSentence(d2)

f1 = open("tmp/xml1","w")
f1.write(XML1)
f1.close()
f2 = open("tmp/xml2","w")
f2.write(XML2)
f2.close()


##Find diff between the xmls
import subprocess
import os

cmd = ['cat', os.getcwd()+'/tmp/xml1', os.getcwd()+'/tmp/xml2']

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         cwd=os.getcwd()
                         )
    return p.stdout

output = "".join(run_command("xmldiff tmp/xml1 tmp/xml2".split()).readlines())
import re
moves = re.findall("{{(.*?)}}",output, re.DOTALL)
final_moves = []
for k in moves: final_moves.append(k.split(";;;"))

##final_set of moves figured out and stored in final_moves

#Read the XML files to simulate the moves
f1 = open("tmp/xml1","r")
f2 = open("tmp/xml2","r")
from lxml import etree
xml1 = etree.parse(f1)
xml2 = etree.parse(f2)

## Now analyze the moves and release events


# Simulating the moves

from helperFuncs import *
# Case 1 : 
# Nodes/ChunkNodes at one level combine to form a chunk
def checkForChunking():
	newChunks = {}
	removedChunks = {}
	newNode = {}
	removedNode = {}
	movedNode = {}
	movedChunks = {}

	nodeChanged = {}


	def analyzeNewElem(newElem):
		#Analyze
		if(newElem.tag=="chunkNode"):
			#Case : Addition of ChunkNode
			newChunks[newElem.get('id')] = newElem
		else:
			#Case Addition of Node
			newNode[newElem.get('id')] = newElem

	def analyzeMovedElem(oldElem, newElem):
		#Analyze
		if(newElem.tag=="chunkNode"):
			#Case : Addition of ChunkNode
			movedChunks[newElem.get('id')] = {'old': oldElem , 'new' : newElem}
		else:
			#Case Addition of Node
			movedChunks[newElem.get('id')] = {'old': oldElem , 'new' : newElem}		

		#print toString(newElem)
		#print toString(oldElem)

	def analyzeRemovedElem(removedElem):
		#Analyze
		if(removedElem.tag=="chunkNode"):
			#Case : Addition of ChunkNode
			removedChunks[removedElem.get('id')] = removedElem
		else:
			#Case Addition of Node
			removedNode[removedElem.get('id')] = removedElem

	def attrChanged(xpath):
		xpath = xpath.split("/")
		if "chunkNode" in xpath[-2]:
			#Case ChunkNode changed
			foo = 1
		else:
			#Case node changed
			# Add to nodeChanged
			nodeChanged[xml1.xpath("/".join(xpath[:-1]))[0].get('id')] = 1


	for k in final_moves:
		print "="*80
		# print newChunks
		print "Operationg Details :: ",k, "\n"
		move = k[0]
		if move == "append-first":
			appendFirst(xml1, k[1], k[2])
			#Analyze
			analyzeNewElem(deepcopy(etree.XML(k[2])))

		if move == "insert-after":
			insertAfter(xml1,k[1], k[2])
			#Analyze
			analyzeNewElem(deepcopy(etree.XML(k[2])))


		if move == "move-first":
			if not ("@" in k[1]):
				oldElem = deepcopy(xml1.xpath(k[1])[0])
				moveFirst(xml1, k[1], k[2])
				newElem = deepcopy(list(xml1.xpath(k[2])[0])[0])
				analyzeMovedElem(oldElem,newElem)
			else:
				attrChanged(k[1])	

		if move == "move-after":
			if not ("@" in k[1]):
				oldElem = deepcopy(xml1.xpath(k[1])[0])
				moveAfter(xml1, k[1], k[2])
				newElem = xml1.xpath(k[2])[0].getnext()
				analyzeMovedElem(oldElem,newElem)
			else:
				attrChanged(k[1])	

		if move == "remove":
			if not ("@" in k[1]):
				# Note : Only chunkNodes will be removed in our SSF usecase.
				#Analyze
				analyzeRemovedElem(deepcopy(xml1.xpath(k[1])[0]))

				remove(xml1, k[1])
			else:
				attrChanged(k[1])				

		# print newChunks

	# print removedChunks
	# print movedChunks

	for k in final_moves:
		print k
	return


	oldXML = etree.parse(open("tmp/xml1","r"))

	## NER -> Chunker Merger
	## In case of a removed chunk
	## Find the node(s) under the removed chunk(s) in the initial xml
	## and add a chunk encapsulating the same nodes in the final xml
	for k in removedChunks.keys():
		chunk = oldXML.xpath("//chunkNode[@id='"+k+"']")[0]
		children = list(chunk)

		## Search all children in the target XML and encapsulate them 
		## with the given removedChunk
		## Remove the individual after merging it with final node 
		index = 0
		for n in children:
			index+=1
			if n.tag=="node":
				oldNode = oldXML.xpath("//node[@id='"+n.get('id')+"']")[0]
				newNode = xml2.xpath("//node[@id='"+n.get('id')+"']")[0]
			if n.tag=="chunkNode":
				oldNode = oldXML.xpath("//chunkNode[@id='"+n.get('id')+"']")[0]
				newNode = xml2.xpath("//chunkNode[@id='"+n.get('id')+"']")[0]

			mergedNode = nodeMerge( oldNode, newNode )
			oldNode.addnext(mergedNode)

			if index==len(children):
				#Add the oldChunk to the newXMl and them remove
				newNode.addnext(oldXML.xpath("//chunkNode[@id='"+k+"']")[0])
				for p in children:
					xml2.xpath("//chunkNode[@id='"+k+"']")[0].append(xml2.xpath("//node[@id='"+p.get('id')+"']")[0])
			oldNode.getparent().remove(oldNode)
			
		##Merge Node attribute changes
		for nodeChange in nodeChanged.keys():
			newNode = xml2.xpath("//node[@id='"+nodeChange+"']")[0]
			newNode.addnext(nodeMerge(etree.parse(open("tmp/xml1","r")).xpath("//node[@id='"+nodeChange+"']")[0], newNode))
			newNode.getparent().remove(newNode)

checkForChunking()
print "="*80
print "SOURCE !!"
print toString(etree.parse(open("tmp/xml1","r")))
print "="*80
print "Target !!"
print toString(etree.parse(open("tmp/xml2","r")))
print "="*80
print "MERGED !!"
print toString(xml2)


# from xmldiff import main as XMLDIFF_MAIN

# f1 = "tmp/xml1"
# f2 = "tmp/xml2"

# html = 0
# xupd, ezs, verbose = 0, 0, 0
# norm_sp, include_comment, ext_ges, ext_pes = 1, 1, 0, 0
# encoding = 'UTF-8'
# XMLDIFF_MAIN.process_files(f1, f2, norm_sp, xupd, ezs, verbose, ext_ges, ext_pes, include_comment, encoding, html)

# d1 = SSF.Document("test_data/small/sentence.0.shallowParse.wx")
# for sen in d1.nodeList:
# 	sen.assignNames()
# print sen.getXML()
# SSF.assignNodeNames(d1)

