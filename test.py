#!/usr/bin/env python
#-*- coding:utf-8 -*-

from codegen import to_source
from std import stdScope
from translator import *

testFile = './extern/Building.php'

def generate(file):
	processor = Processor(stdScope)
	phpAst = getPHPAst(file)
	pythonAst = processor.translate(phpAst)
	print to_source(pythonAst)

#print to_source(ast.ClassDef('Test', (ast.Name('A', ()), ast.Name('B', ())), [ast.Assign([ast.Name('x', ())], ast.Num(4))], ()))

generate(testFile)