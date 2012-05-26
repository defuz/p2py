#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast
from translator import Scope

stdScope = Scope()

@stdScope.registerTranslator
def Name(processor, node):
	# Name(identifier id, expr_context ctx)
	return ast.Name(node.parts[0], [])

@stdScope.registerTranslator
def Stmt_Class(processor, node):
	# ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
	extends = [processor.process(node.extends)] if node.extends else [ast.Name('object', [])]
	stmts = processor.process(node.stmts) if node.stmts else ast.Pass()
	return ast.ClassDef(node.name, extends, stmts, [])

@stdScope.registerTranslator
def Stmt_ClassMethod(processor, node):
	# FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
	args = [ast.Name('self', [])] + processor.process(node.params)
	arguments = ast.arguments(args=args, vararg=None, kwarg=None, defaults=[ast.Name('self', [])])
	body = processor.process(node.stmts)
	return ast.FunctionDef(node.name, arguments, body, [])

@stdScope.registerTranslator
def Scalar_LNumber(processor, node):
	# Num(object n)
	return ast.Num(node.value)

@stdScope.registerTranslator
def Scalar_String(processor, node):
	# Str(string s)
	return ast.Str(node.value)

@stdScope.registerTranslator
def Const(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	return ast.Assign([ast.Name(node.name, [])], processor.process(node.value))

@stdScope.registerTranslator
def Stmt_ClassConst(processor, node):
	return processor.process(node.consts)[0]

@stdScope.registerTranslator
def Expr_ClassConstFetch(processor, node):
	if node['class'].parts[0] == 'self':
		return ast.Name(node.name, [])
	return ast.Attribute(processor.process(node['class']), node.name)

@stdScope.registerTranslator
def Expr_Array(processor, node):
	# Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
	# Dict(expr* keys, expr* values)
	# Name(identifier id, expr_context ctx)
	keys, values = zip(*((item.key, item.value) for item in node.items))
	return ast.Call(
		ast.Name('OrderedDict', []),
		[ast.Dict(processor.process(keys), processor.process(values))],
		[], None, None
	)

@stdScope.registerTranslator
def Stmt_PropertyProperty(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	return ast.Assign([ast.Name(node.name, [])], processor.process(node.default))

@stdScope.registerTranslator
def Stmt_Property(processor, node):
	return processor.process(node.props)[0]
