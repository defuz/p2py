#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast
from base import *
from itertools import repeat

class PHPNode(Dict):
	def __str__(self):
		def valueToStr(value, deep):
			if isinstance(value, dict):
				if not deep:
					return '<' + value.get('_', '?') + '>'
				node = value.copy()
				return '<' + node.pop('_', '?') + ': ' + ', '.join(key + ': ' + valueToStr(value, deep - 1) for key, value in node.items()) + '>'
			if isinstance(value, list):
				if not deep:
					return '[...]'
				return '[' + ', '.join(valueToStr(v, deep - 1) for v in value) + ']'
			return str(value)
		return valueToStr(self, 3)

def getPHPAst(file):
	result = os.popen("php ast.php " + file).read()
	if result.startswith('Parse Error'):
		raise Exception(result)
	return json(result, PHPNode)


class Scope(object):

	def __init__(self):
		self.translators = {}

	def registerTranslator(self, func):
		self.translators[func.__name__] = func
		return func

	def registerClassTranslator(self, cls):
		for method in cls.__dict__:
			self.registerTranslator(method)
		return cls

	def defaultTranslator(self, processor, node):
		return '# ' + str(node)

	def getTranslator(self, node):
		return self.translators.get(node._, self.defaultTranslator)
		

class Processor(object):

	def __init__(self, scope):
		self.scope = scope

	def process(self, node):
		if isinstance(node, (list, tuple)):
			return [self.process(n) for n in node]
		return self.scope.getTranslator(node)(self, node)

	def translate(self, nodes):
		return ast.Module(self.process(nodes))
