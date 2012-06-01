#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast

from simply_ast import *
from scope import statement

@statement
def Expr_ClassConstFetch(processor, node):
	if node['class'].parts[0] == 'self':
		return idnt(node.name)
	return attr(processor, node['class'], node.name)

@statement
def Expr_PropertyFetch(processor, node):
	return attr(processor, node.var, node.name)

@statement
def Expr_ConstFetch(processor, node):
	return processor.process(node.name)

@statement
def Expr_Variable(processor, node):
	return idnt(node.name)

@statement
def Expr_Assign(processor, node):
	# xxx: $a[] = 42
	if node.var._ == 'Expr_ArrayDimFetch' and node.var.dim is None:
		return call(attr(processor, node.var.var, 'append'), [processor.process(node.expr)])
	# todo: $this->$name = $value as setattr
	return ast.Assign([processor.process(node.var)], processor.process(node.expr))

@statement
def Expr_AssignRef(processor, node):
	return Expr_Assign(processor, node) # todo: make the difference

@statement
def Expr_Isset(processor, node):
	# todo: use context for isset!
	# Compare(expr left, cmpop* ops, expr* comparators)
	return ast.Compare(processor.process(node.vars[0]), [ast.IsNot()], [idnt('None')])

@statement
def Expr_Ternary(processor, node):
	# IfExp(expr test, expr body, expr orelse)
	return ast.IfExp(processor.process(node.cond), processor.process(node['if']), processor.process(node['else']))

@statement
def Expr_StaticPropertyFetch(processor, node):
	# Attribute(expr value, identifier attr, expr_context ctx)
	if node['class'].parts[0] == 'self':
		return idnt(node.name)
	return attr(processor, node['class'], node.name)

@statement
def Expr_ArrayDimFetch(processor, node):
	# Subscript(expr value, slice slice, expr_context ctx)
	return ast.Subscript(processor.process(node.var), processor.process(node.dim), [])

@statement
def Arg(processor, node):
	return processor.process(node.value)

@statement
def Expr_FuncCall(processor, node):
	return call(processor.process(node.name), processor.process(node.args))

@statement
def Expr_MethodCall(processor, node):
	return call(attr(processor, node.var, node.name), processor.process(node.args))

@statement
def Expr_StaticCall(processor, node):
	if node['class'].parts[0] == 'self':
		return call(idnt(node.name), processor.process(node.args))
	return call(attr(processor, node['class'], node.name), processor.process(node.args))

@statement
def Expr_Array(processor, node):
	# Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
	# Dict(expr* keys, expr* values)
	# Name(identifier id, expr_context ctx)
	keys, values = zip(*((item.key, item.value) for item in node.items)) if node.items else ([], [])
	if not any(keys):
		return ast.List(processor.process(values), [])
	if not all(keys):
		from itertools import count
		c = count()
		keys = [processor.process(i) if i else ast.Num(c.next()) for i in keys]
	else:
		keys = processor.process(keys)
	return ast.Dict(keys, processor.process(values))

@statement
def Expr_Empty(processor, node):
	return ast.UnaryOp(ast.Not(), processor.process(node.var))

@statement
def Expr_New(processor, node):
	# Call(expr func, expr* args, keyword* keywords,expr? starargs, expr? kwargs)
	return call(processor.process(node['class']), processor.process(node.args))

@statement
def Expr_Instanceof(processor, node):
	# Call(expr func, expr* args, keyword* keywords,expr? starargs, expr? kwargs)
	return call(idnt('isinstance'), [processor.process(node.expr)] + [processor.process(node['class'])])

@statement
def Expr_ErrorSuppress(processor, node):
	# TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
	# ExceptHandler(expr? type, expr? name, stmt* body)
	return ast.TryExcept([processor.process(node.expr)], [ast.ExceptHandler(idnt('BaseException'), None, [ast.Pass()])], [])

#### casts ####

@statement
def Expr_Cast_Int(processor, node):
	return call(idnt('int'), [processor.process(node.expr)])

@statement
def Expr_Cast_Double(processor, node):
	return call(idnt('float'), [processor.process(node.expr)])

# todo: implement other casts
