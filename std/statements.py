#!/usr/bin/env python
#-*- coding:utf-8 -*-

import copy

from simply_ast import *
from scope import syntax

@syntax
def Name(processor, node):
	# Name(identifier id, expr_context ctx)
	return idnt(node.parts[0])

@syntax
def Const(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	return ast.Assign([idnt(node.name)], processor.process(node.value))

@syntax
def File(processor, node):
	return ast.Module(processor.process(node.stmts))

@syntax
def Stmt_Class(processor, node):
	# ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
	extends = [processor.process(node.extends)] if node.extends else [idnt('object')]
	stmts = processor.process(node.stmts) if node.stmts else ast.Pass()
	return ast.ClassDef(node.name, extends, stmts, [])

@syntax
def Stmt_ClassMethod(processor, node):
	# FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
	names, defaults = map(list,
		zip(*(
		(idnt(item.name), processor.process(item.default) if item.default else None) for item in node.params)
		)
	) if node.params else ([], [])
	isStatic = node.type & 8
	args = [idnt('self')] + names if not isStatic else names
	arguments = ast.arguments(args=args, vararg=None, kwarg=None, defaults=[None] + defaults)
	body = processor.process(node.stmts) if node.stmts else [ast.Pass()]
	decorators = [idnt('staticmethod')] if isStatic else []
	return ast.FunctionDef(node.name, arguments, body, decorators)

@syntax
def Stmt_Return(processor, node):
	return ast.Return(processor.process(node.expr) if node.expr else None)

@syntax
def Stmt_ClassConst(processor, node):
	return processor.process(node.consts)[0]

@syntax
def Stmt_PropertyProperty(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	# xxx: class property without default value
	if node.default:
		return ast.Assign([idnt(node.name)], processor.process(node.default))
	else:
		return str('# ' + node.name)

@syntax
def Stmt_Property(processor, node):
	return processor.process(node.props)[0]

@syntax
def Stmt_Echo(processor, node):
	return ast.Print(None, processor.process(node.exprs), True)

@syntax
def Stmt_If(processor, node):
	# If(expr test, stmt* body, stmt* orelse)
	ifnodes = node.elseifs[::-1] + [node]
	elsestmts = processor.process(getattr(node['else'], 'stmts', []))
	return reduce(lambda r, n: [ast.If(processor.process(n.cond), processor.process(n.stmts), r)], ifnodes, elsestmts)[0]

@syntax
def Stmt_Foreach(processor, node):
	if not node.keyVar:
		return ast.For(processor.process(node.valueVar), processor.process(node.expr), processor.process(node.stmts), None)
	# todo: enumerate(expr) or expr.items() ?
	target = ast.Tuple(processor.process([node.keyVar,node.valueVar]), [])
	expr = call(attr(processor, node.expr, 'items'), [])
	return ast.For(target, expr, processor.process(node.stmts), None)

@syntax
def Stmt_Switch(processor, node):
	def pred_group(predicate, iterable):
		groups = []
		for x in iterable:
			if predicate(x):
				groups[-1].append(x)
			else:
				groups.append([x])
		if not groups[0]:
			groups.pop(0)
		return groups
	groups = pred_group(lambda case: not case.stmts, node.cases[::-1])
	def merge_cond(cases):
		result = copy.deepcopy(cases[0])
		result.cond = []
		for case in cases[::-1]:
			if case.cond:
				result.cond.append(case.cond)
		result.cond = result.cond if len(result.cond) > 1 else result.cond[0]
		return result
	groups = map(lambda group: group.pop() if len(group) == 1 else merge_cond(group), groups)

	if node.cond._ == 'Expr_Assign':
		value, prepend = processor.process(node.cond.var), processor.process(node.cond)
	elif node.cond._ != 'Expr_Variable':
		value, prepend = processor.process(node.cond), None
	else:
		value = idnt('switch_value')
		prepend = ast.Assign([value], processor.process(node.cond))

	def compare_value(condition):
		return ast.Compare(value, [ast.Eq()], [processor.process(condition)])
	def make_if(r, n):
		condition = ast.BoolOp(ast.Or(), map(compare_value, n.cond)) if isinstance(n.cond, list) else compare_value(n.cond)
		if n.stmts[-1]._ == 'Stmt_Break':
			return ast.If(condition, processor.process(n.stmts[:-1]), r if isinstance(r, list) else [r])
		return [ast.If(condition, processor.process(n.stmts), []), r]

	default = [case for case in groups if not case.cond]
	default = (default[0].stmts[:-1] if default[0].stmts[-1]._ == 'Stmt_Break' else default[0].stmts) if default else []

	ifs = reduce(make_if, [case for case in groups if case.cond], processor.process(default))
	return [prepend] + ifs if prepend else ifs

@syntax
def Stmt_For(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	loop = ast.While(
		processor.process(node.cond)[0] if node.cond else idnt('True'),
		processor.process(node.stmts) + processor.process(node.loop),
		[]
	)
	return processor.process(node.init) + [loop] if node.init else loop

@syntax
def Stmt_While(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	return ast.While(processor.process(node.cond), processor.process(node.stmts), [])

@syntax
def Stmt_Do(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	# If(expr test, stmt* body, stmt* orelse)
	return ast.While(idnt('True'), processor.process(node.stmts) + [ast.If(
		ast.UnaryOp(ast.Not(), processor.process(node.cond)), [ast.Break()], []
	)], [])

@syntax
def Stmt_Break(processor, node):
	if node.num and node.num > 1:
		raise NotImplementedError("Couldn't break more than one loop")
	return ast.Break()

@syntax
def Stmt_Continue(processor, node):
	if node.num and node.num > 1:
		raise NotImplementedError("Couldn't continue more than one loop")
	return ast.Continue()

@syntax
def Stmt_Throw(processor, node):
	# Raise(expr? type, expr? inst, expr? tback)
	return ast.Raise(processor.process(node.expr), None, None)

@syntax
def Stmt_TryCatch(processor, node):
	# TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
	# ExceptHandler(expr? type, expr? name, stmt* body)
	catches = [ast.ExceptHandler(processor.process(catch.type), idnt(catch.var), processor.process(catch.stmts))
	                for catch in node.catches]
	return ast.TryExcept(processor.process(node.stmts), catches, [])

@syntax
def Stmt_Unset(processor, node):
	# todo: unset($this->$name) as delattr
	return ast.Delete(processor.process(node.vars))