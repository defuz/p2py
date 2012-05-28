#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import Counter
from operator import add
from base import progress
from php import getPHPAst, findFiles

def reprCounter(counter):
	items = [(count, name) for name, count in counter.items()]
	return '\n'.join("%s: %s" % (n, c) for c, n in reversed(sorted(items)))

def analizeFuncCall(file):
	try:
		ast = getPHPAst(file)
		funcCalls = reduce(add, (node.find('Expr_FuncCall') for node in ast), [])
		return Counter(call.name.parts[0] for call in funcCalls)
	except: # todo:fix
		print 'analizeFuncCall talk that something was wrong with file %s ' % file
		return Counter()

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		print("Please specify project pass")
		sys.exit(1)
	funcCalls = reduce(add, (analizeFuncCall(f) for f in progress(findFiles(sys.argv[1], '.php'))), Counter())
	print reprCounter(funcCalls)