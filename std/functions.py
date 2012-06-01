#!/usr/bin/env python
#-*- coding:utf-8 -*-

from simply_ast import *
from scope import function

@function
def in_array(processor, node):
	return ast.Compare(processor.process(node.args[0]), [ast.In()], [processor.process(node.args[1])])

