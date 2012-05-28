#!/usr/bin/env python
#-*- coding:utf-8 -*-

from codegen import to_source
from std import stdScope
from translator import *
from php import getPHPAst

def generate(file):
	processor = Processor(stdScope)
	phpAst = getPHPAst(file)
	pythonAst = processor.translate(phpAst)
	return to_source(pythonAst)

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		print("Please specify filename")
		sys.exit(1)

	print generate(sys.argv[1])


