#!/usr/bin/env python
#-*- coding:utf-8 -*-

from simply_ast import *
from scope import function

@function
def count(processor, node):
	return call(idnt('len'), processor.process(node.args))

@function
def in_array(processor, node):
	return ast.Compare(processor.process(node.args[0]), [ast.In()], [processor.process(node.args[1])])

@function
def array_push(processor, node):
	if len(node.args) == 2:
		return call(attr(processor, node.args[0], 'append'), [processor.process(node.args[1])])
	if node.args > 2:
		return call(attr(processor, node.args[0], 'extend'), [ast.List(processor.process(node.args[1:]), [])])

@function
def array_pop(processor, node):
	return call(attr(processor, node.args[0], 'pop'), [])

@function
def is_array(processor, node):
	# xxx: dict and tuple is array :(
	return call(idnt('isinstance'), [processor.process(node.args[0]), idnt('list')])

@function
def array_filter(processor, node):
	if len(node.args) == 1:
		return call(idnt('filter'), [idnt('None'), processor.process(node.args[0])])
	if len(node.args) == 2:
		return call(idnt('filter'), processor.process(node.args[::-1]))


@function
def array_merge(processor, node):
	# xxx: for dict use dict1.update(dict2)
	return ast.BinOp(processor.process(node.args[0]), ast.Add(), processor.process(node.args[1:]))

@function
def array_map(processor, node):
	return call(idnt('map'), processor.process(node.args))

@function
def array_values(processor, node):
	return call(attr(processor, node.args[0], 'values'), [])

@function
def array_keys(processor, node):
	return call(attr(processor, node.args[0], 'keys'), [])

@function
def array_shift(processor, node):
	return call(attr(processor, node.args[0], 'pop'), [ast.Num(0)])

@function
def array_slice(processor, node):
	start = processor.process(node.args[1])
	if len(node.args) > 2:
		finish = ast.BinOp(start, ast.Add(), [processor.process(node.args[2])])
	else:
		finish = None
	return ast.Subscript(processor.process(node.args[0]), ast.Slice(start, finish, None), [])

@function
def array_diff(processor, node):
	# xxx: set only!
	return ast.BinOp(processor.process(node.args[0]), ast.Sub(), processor.process(node.args[1:]))

@function
def array_unshift(processor, node):
	if len(node.args) == 2:
		return call(attr(processor, node.args[0], 'insert'), [ast.Num(0), processor.process(node.args[1])])
	# todo: myList[:0] = [var1, var2, ...]

@function
def array_search(processor, node):
	return call(attr(processor, node.args[1], 'index'), [processor.process(node.args[0])])

##todo: array_uintersect: 2
##todo: array_splice:
##   myList[offset : offset+length] = replacement
##   # without replacement:
##   del myList[offset : offset+length]
##todo: array_unique, set?
##array_search: 1
#
