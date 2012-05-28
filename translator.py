#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast

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
			result = []
			for n in node:
				r = self.process(n)
				if isinstance(r, (list, tuple)):
					result.extend(r)
				else:
					result.append(r)
			return result
		return self.scope.getTranslator(node)(self, node)

	def translate(self, node):
		return self.process(node)
