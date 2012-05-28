#!/usr/bin/env python
#-*- coding:utf-8 -*-

from base import *

class PHPNode(Dict):
	def find(self, type):
		result = []
		if self.get('_', '?') == type:
			result.append(self)
		for item in self.values():
			if isinstance(item, PHPNode):
				result.extend(item.find(type))
			elif isinstance(item, (tuple, list)):
				for i in item:
					if isinstance(i, PHPNode):
						result.extend(i.find(type))
		return result

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
	return PHPNode(_='File', stmts=json(result, PHPNode))

def findFiles(top, extention = '.php'):
	import os
	for root, dirs, files in os.walk(top):
		for file in files:
			if file.endswith(extention):
				yield os.path.join(root, file)