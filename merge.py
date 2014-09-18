# -*- coding: utf-8 -*-
#!/usr/bin/env python

import SSF
import sys
from copy import deepcopy

from lxml import etree

from helperFuncs import *

d1 = SSF.Document(sys.argv[1]) # NER
d2 = SSF.Document(sys.argv[2]) # MWE
d3 = SSF.Document(sys.argv[3]) # Chunker


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



def NER_CHUNKER_MERGE(d1,et):
	# def NER_CHUNKER_MERGE():
	t = getXMLofFirstSentence(d1)

	source = et
	target = etree.XML(t)
	merged = etree.XML(t)

	#Find all nodes in source of attr_etype="ne"
	added_nerChunks = source.xpath("//chunkNode[@attr_etype='ne_mwe']")
	modified_nerNodes = source.xpath("//node[@attr_etype='ne_mwe']")

	# 1. Condition : MWE/NER is a subset of Chunk
	#   Decision  : New Chunk engulfs NER/MWE

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

	## All modified_nerNodes are children of all the added ner toplevel Chunks
	## Just addition of structural information in the chunker
	## and all modified tokens in the output are assumed to be 
	## at the same level
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

	##
	# If after the previous step, the structure of the ner output ate up a chunk 
	# defined by the chunker, that chunk will be empty in the merged node !!
	#
	# Action :: Look for all empty chunks in the current merged sentence,
	#           Remove them !! 
	# 	        as the structure given my NER is to be given higher priority

	for chunkNode in merged.xpath(".//chunkNode"):
		#print toString(chunkNode)
		if len(list(chunkNode)) == 0:
			chunkNode.getparent().remove(chunkNode)

	merged  = set_new_etype(merged,"ne_mwe_chunker")

	return merged


def merge_NER_MWE(d1,d2):
	###Condition 5 and 6 
	## Merge NER and MWE first

	ner = getXMLofFirstSentence(d1)
	mwe = getXMLofFirstSentence(d2)

	merged = getXMLofFirstSentence(d2)

	# s = open("tmp/xml1.xml","r").read()
	# t = open("tmp/xml2.xml","r").read()

	ner = etree.XML(ner)
	mwe = etree.XML(mwe)
	merged = etree.XML(merged)

	sentenceId = ner.attrib['id']

	added_nerChunks = ner.xpath("//chunkNode[@attr_etype='ne']")
	added_mweChunks = mwe.xpath("//chunkNode[@attr_etype='mwe']")

	lengthOfNodes = len(merged.xpath("//node"))
	before = ["None"]*lengthOfNodes
	after = ["None"]*lengthOfNodes

	for chunk in added_nerChunks:
		nodes = chunk.xpath(".//node")
		first_node = nodes[0]
		last_node = nodes[-1]
		if  before[int(first_node.attrib['id'].split("_")[-1])] != "None": 
			before[int(first_node.attrib['id'].split("_")[-1])].append({'operation':'ner' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']})
		else:
			#Initialise
			before[int(first_node.attrib['id'].split("_")[-1])] = [{'operation':'ner' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']}]

		if after[int(last_node.attrib['id'].split("_")[-1])] != "None" : 
			after[int(last_node.attrib['id'].split("_")[-1])].append({'operation':'ner' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']})
		else:
			#Initialise
			after[int(last_node.attrib['id'].split("_")[-1])] = [{'operation':'ner' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']}]

	for chunk in added_mweChunks:
		nodes = chunk.xpath(".//node")
		first_node = nodes[0]
		last_node = nodes[-1]
		if before[int(first_node.attrib['id'].split("_")[-1])] != "None":
			before[int(first_node.attrib['id'].split("_")[-1])].append({'operation':'mwe' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']})
		else:
			#Initialise
			before[int(first_node.attrib['id'].split("_")[-1])] = [{'operation':'mwe' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']}]
			
		if after[int(last_node.attrib['id'].split("_")[-1])] != "None":
			after[int(last_node.attrib['id'].split("_")[-1])].append({'operation':'mwe' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']})
		else:
			#Initialise
			after[int(last_node.attrib['id'].split("_")[-1])] = [{'operation':'mwe' , 'phrase_len':len(chunk.attrib['phrase']), 'id' : chunk.attrib['id']}]


	##iterate over before and after and sort the chunks brackets by length of phrase
	for b in before:
		if b != "None":
			b = sorted(b, key = lambda k : k['phrase_len'])	

	##iterate over  after and sort the chunks brackets by length of phrase
	for b in after:
		if b != "None":
			b = sorted(b, key = lambda k : -1 * k['phrase_len'])	

	newSentence = etree.XML("<Sentence id='"+sentenceId+"'></Sentence>")
	context = [newSentence]

	bracket = {}
	bracket["mwe"] = {"open":"{","close":"}"}
	bracket["ner"] = {"open":"(","close":")"}
	bracket["chunker"] = {"open":"[","close":"]"}

	for i in range(len(before)):
		########################3
		# ### Print debug output
		# if(before[i])!="None":
		# 	for k in before[i]:		
		# 		print bracket[k["operation"]]["open"]+k['operation']+"_"+k['id']+" ",	

		# print sentenceId+"_"+str(i)+" ",

		# if(after[i]) != "None":
		# 	for k in after[i]:
		# 		print k['operation']+"_"+k['id']+bracket[k["operation"]]["close"]+" ",

		##Print debug output end

		if(before[i])!= "None":
			for k in before[i]:
				if(k['operation']=="ner"):
					newChunk = chunkSkeleton(ner.xpath("//chunkNode[@id='"+k['id']+"']")[0])
					context[-1].append(newChunk)
					context.append(newChunk)
				if(k['operation']=="mwe"):
					newChunk = chunkSkeleton(mwe.xpath("//chunkNode[@id='"+k['id']+"']")[0])
					context[-1].append(newChunk)
					context.append(newChunk)

		context[-1].append(nodeMerge(ner.xpath("//node[@id='"+sentenceId+"_"+str(i)+"']")[0], mwe.xpath("//node[@id='"+sentenceId+"_"+str(i)+"']")[0]))

		if(after[i])!= "None":
			for k in after[i]:
				##TO-DO::: Check for conflicts
				## Assumption :: No conflicts in NER - MWE 	
				# if(context[-1].attrib['attr_etype']==k['operation']):
				context.pop(-1)


	newSentence = set_new_etype(newSentence,"ne_mwe")

	return newSentence


## First merge NER and MWE to figure out the smaller chunks
## and then impose these on the chunker structure
merged = merge_NER_MWE(d1,d2)
merged = NER_CHUNKER_MERGE(d3, merged)
print SSF.XML_TO_SSF(merged)
# print toString(merged)
