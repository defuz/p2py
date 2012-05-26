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
	extends = [processor.process(node.extends)]
	stmts = processor.process(node.stmts) if node.stmts else ast.Pass()
	return ast.ClassDef(node.name, extends, stmts, [])

@stdScope.registerTranslator
def Stmt_ClassMethod(processor, node):
	# FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
	args = [ast.Name('self', [])] + processor.process(node.params)
	arguments = ast.arguments(args=args, vararg=None, kwarg=None, defaults=[])
	body = processor.process(node.stmts)
	return ast.FunctionDef(node.name, arguments, body, [])

