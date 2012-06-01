#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast

from simply_ast import *
from scope import statement

@statement
def Scalar_LNumber(processor, node):
	# Num(object n)
	return ast.Num(node.value)

@statement
def Scalar_DNumber(processor, node):
	# Num(object n)
	return ast.Num(float(node.value))

@statement
def Scalar_String(processor, node):
	# Str(string s)
	return ast.Str(node.value)

@statement
def Scalar_LineConst(processor, node):
	# inspect.currentframe().f_back.f_lineno
	return ast.parse('inspect.currentframe().f_back.f_lineno')

@statement
def Scalar_FuncConst(processor, node):
	# inspect.currentframe().f_code.co_name
	return ast.parse('inspect.currentframe().f_code.co_name')

@statement
def Scalar_FileConst(processor, node):
	# inspect.currentframe().f_code.co_filename
	return ast.parse('inspect.currentframe().f_code.co_filename')

@statement
def Scalar_ClassConst(processor, node):
	# inspect.currentframe().f_method.im_class
	return ast.parse('inspect.currentframe().f_method.im_class')

@statement
def Scalar_Encapsed(processor, node):
	parts = [elem.replace('%', '%%') if isinstance(elem, basestring) else '%s' for elem in node.parts]
	vars = [elem for elem in node.parts if not isinstance(elem, basestring)]
	params = ast.Tuple(processor.process(vars), []) if len(vars) > 1 else processor.process(vars[0])
	return ast.BinOp(ast.Str(''.join(parts)), ast.Mod(), params)