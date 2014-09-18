# -*- coding: utf-8 -*-
#!/usr/bin/env python

import SSF
import sys
from copy import deepcopy

from lxml import etree

from helperFuncs import *

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

# for node in d1.nodeList:
# 	print node.getXML()



def NER_CHUNKER_MERGE(d1,d2):
	# def NER_CHUNKER_MERGE():
	s = getXMLofFirstSentence(d1)
	t = getXMLofFirstSentence(d2)

	# s = open("tmp/xml1.xml","r").read()
	# t = open("tmp/xml2.xml","r").read()


	source = etree.XML(s)
	target = etree.XML(t)
	merged = etree.XML(t)

	##debug
	# open("tmp/xml1.xml","w").write(toString(source))
	# open("tmp/xml2.xml","w").write(toString(target))
	##debug end

	#Find all nodes in source of attr_etype="ne"
	added_nerChunks = source.xpath("//chunkNode[@attr_etype='ne']")
	modified_nerNodes = source.xpath("//node[@attr_etype='ne']")

	chunkChildren = []
	nodeChildren = []


	for chunk in added_nerChunks:
		if chunk not in chunkChildren:
			childChunkNodes = chunk.xpath(".//chunkNode")
			# Remove all child nodes from added_nerChunks
			# The iteration goes from top to bottom
			# Hence no conflict
			for c in childChunkNodes: chunkChildren.append(c)

			childNodes = chunk.xpath(".//node")
			for c in childNodes: nodeChildren.append(c)

	##Pruning added chunkList	
	pruned_added_nerChunks = [x for x in added_nerChunks if x not in chunkChildren]

	##Stats collected !!
	## Logic Layer starts !!

	## Case 1 ::
	## All modified_nerNodes are children of all the added ner toplevel Chunks
	## Just addition of structural information in the chunker
	## and all modified tokens in the output are assumed to be 
	## at the same level
	print nodeChildren
	print modified_nerNodes
	if set(nodeChildren) == set(modified_nerNodes):
		##Iterate over pruned added chunkList
		for chunk in pruned_added_nerChunks:
			## For each chunk find the first node and add this chunk next to the corresponding node in merged tree
			
			childNode = chunk.xpath(".//node")
			first_node_id = childNode[0].get('id')
			
			## Iterate over all the child nodes 
			## and merge the individual nodes in both the files
			targetNodesList = []
			for child in childNode:
				target_node = merged.xpath("//node[@id='"+child.get('id')+"']")[0]
				targetNodesList.append(target_node)
				child = nodeMerge(child, target_node)

			node_in_merged = merged.xpath("//node[@id='"+first_node_id+"']")[0]
			node_in_merged.addnext(chunk)
			# node_in_merged.getparent().remove(node_in_merged)

			##Remove Duplicate Copies of target_node
			for target_node in targetNodesList:
				target_node.getparent().remove(target_node)

		return merged

merged = NER_CHUNKER_MERGE(d1,d2)
# merged = NER_CHUNKER_MERGE()

print SSF.XML_TO_SSF(merged)
# print toString(merged)
