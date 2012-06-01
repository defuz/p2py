#!/usr/bin/env python
#-*- coding:utf-8 -*-

def defaultStatementTranslator(processor, node):
		return '# ' + str(node)

class Scope(object):

	def __init__(self):
		self.translators = {}
		self.functions = {}

	def registerModule(self, module):
		for name, item in module.__dict__.items():
			if hasattr(item, '__statement__'):
				self.translators[name] = item
			if hasattr(item, '__function__'):
				self.functions[name] = item

	def getTranslator(self, node):
		return self.translators.get(node._, defaultStatementTranslator)


def statement(func):
	func.__statement__ = True
	vars()['___' + func.__name__] = func
	return func

def function(func):
	func.__function__ = True
	vars()['___' + func.__name__] = func
	return func
