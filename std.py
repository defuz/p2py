#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast
from translator import Scope

stdScope = Scope()

@stdScope.registerTranslator
def Stmt_Class(processor, node):
	# ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
#	extends =
	stmts = [processor.process(stmt) for stmt in node.stmts] if node.stmts else ast.Pass()
	return ast.ClassDef(node.name, [], stmts, [])