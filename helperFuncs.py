# -*- coding: utf-8 -*-
from lxml import etree

def toString(tree):
	if isinstance(tree,basestring):
		return tree
	else:
		return etree.tostring(tree, pretty_print=True)

def nodeMerge(nodeSource, nodeTarget):
	newAttrib = {}
	for k in nodeSource.attrib.keys():
		newAttrib[k] = nodeSource.attrib[k]

	for k in nodeTarget.attrib.keys():
		newAttrib[k] = nodeTarget.attrib[k]

	for k in nodeSource.attrib.keys():
		del nodeSource.attrib[k]	
	for k in newAttrib.keys():
		nodeSource.attrib[k] = newAttrib[k]

	return nodeSource

def chunkSkeleton(chunk):
	output = "<"+chunk.tag+" "
	for k in chunk.attrib.keys():
		output+=k+"='"+chunk.attrib[k]+"' "
	output+="></"+chunk.tag+">"

	return etree.XML(output)

def appendFirst(tree,target, xmlString):
	T = tree.xpath(target)[0]
	T.insert(0,etree.XML(xmlString))

def insertAfter(tree,target, xmlString):
	T = tree.xpath(target)[0]
	T.addnext(etree.XML(xmlString))

def moveFirst(tree, source, target):
	T = tree.xpath(target)[0]
	S = tree.xpath(source)[0]
	T.insert(0,S)

def moveAfter(tree, source, target):
	T = tree.xpath(target)[0]
	S = tree.xpath(source)[0]
	T.addnext(S)

def remove(tree, target):
	T = tree.xpath(target)[0]
	T.getparent().remove(T)

def set_new_etype(tree,etype):

	# Modify the etype to "etype"

	for node in tree.xpath("//*[@attr_etype]"):
		node.attrib['attr_etype']=etype

	return tree

###
## Finds all elements which have the attr_type attribute
## and adds a new attribute called "merger_marker" 
def set_merger_marker(tree,attr_type,mark):

	# Modify the etype to "etype"

	for node in tree.xpath("//*[@"+attr_type+"]"):
		node.attrib['merger_marker']=mark

	return tree

def list_of_children_nodes(tree):
	return tree.xpath("//node")