#!/usr/bin/env python
#-*- coding:utf-8 -*-

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
