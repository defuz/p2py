#!/usr/bin/env python
#-*- coding:utf-8 -*-

class EmptyScope(object):
	def translate(self, processor, node):
		return '# ' + str(node)

class Scope(object):

	def __init__(self, modules, parent = None):
		self.parent = parent or EmptyScope()
		self.translators = []
		map(self.registerModule, modules)

	def registerModule(self, module):
		for name, func in module.__dict__.items():
			if hasattr(func, '__translator_wrapper__'):
				self.translators.append(func(name))

	def translate(self, processor, node):
		for translator in self.translators:
			result = translator(processor, node)
			if result:
				return result
		return self.parent.translate(processor, node)


def syntax(func):
	def wrapper(name):
		def translator(processor, node):
			if node._ == name:
				return func(processor, node)
		return translator
	wrapper.__translator_wrapper__ = True
	return wrapper

def function(func):
	def wrapper(name):
		def translator(processor, node):
			if (node._ == 'Expr_FuncCall'
			and node.name._ == 'Name'
			and len(node.name.parts) == 1
			and node.name.parts[0] == name):
				return func(processor, node)
		return translator
	wrapper.__translator_wrapper__ = True
	return wrapper