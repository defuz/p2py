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
	names, defaults = map(list,
		zip(*(
		(ast.Name(item.name, []), processor.process(item.default) if item.default else None) for item in node.params)
		)
	)
	args = [ast.Name('self', [])] + names
	arguments = ast.arguments(args=args, vararg=None, kwarg=None, defaults=[None] + defaults)
	body = processor.process(node.stmts)
	return ast.FunctionDef(node.name, arguments, body, [])

@stdScope.registerTranslator
def Stmt_Return(processor, node):
	return ast.Return(processor.process(node.expr))

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
def Expr_ConstFetch(processor, node):
	return processor.process(node.name)

@stdScope.registerTranslator
def Expr_Variable(processor, node):
	return ast.Name(node.name, [])

@stdScope.registerTranslator
def Expr_Assign(processor, node):
	return ast.Assign([processor.process(node.var)], processor.process(node.expr))

@stdScope.registerTranslator
def Expr_Isset(processor, node):
	# Compare(expr left, cmpop* ops, expr* comparators)
	return ast.Compare(processor.process(node.vars[0]), [ast.IsNot()], [ast.Name('None', [])])

@stdScope.registerTranslator
def Expr_Ternary(processor, node):
	# IfExp(expr test, expr body, expr orelse)
	return ast.IfExp(processor.process(node.cond), processor.process(node['if']), processor.process(node['else']))

@stdScope.registerTranslator
def Expr_StaticPropertyFetch(processor, node):
	# Attribute(expr value, identifier attr, expr_context ctx)
	if node['class'].parts[0] == 'self':
		return ast.Name(node.name, [])
	return ast.Attribute(processor.process(node['class']), node.name, [])

@stdScope.registerTranslator
def Expr_ArrayDimFetch(processor, node):
	# Subscript(expr value, slice slice, expr_context ctx)
	return ast.Subscript(processor.process(node.var), processor.process(node.dim), [])

@stdScope.registerTranslator
def Arg(processor, node):
	return processor.process(node.value)

@stdScope.registerTranslator
def Expr_FuncCall(processor, node):
	return ast.Call(processor.process(node.name), processor.process(node.args), [], None, None)

@stdScope.registerTranslator
def Expr_StaticCall(processor, node):
	if node['class'].parts[0] == 'self':
		return ast.Call(ast.Name(node.name, []), processor.process(node.args), [], None, None)
	return ast.Call(ast.Attribute(processor.process(node['class']), node.name, []), processor.process(node.args), [], None, None)

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


##### Expr

@stdScope.registerTranslator
def Stmt_Echo(processor, node):
	return ast.Print(None, processor.process(node.exprs), True)


def registerBinaryOp(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.BinOp(processor.process(node.left), pythonOp(), processor.process(node.right))
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)

def registerBoolOp(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.BoolOp(pythonOp(), [processor.process(node.left), processor.process(node.right)])
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)


def registerUnaryOp(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.UnaryOp(pythonOp(), processor.process(node.expr))
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)

def registerCmpOp(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.Compare(processor.process(node.left), [pythonOp()], [processor.process(node.right)])
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)

registerBinaryOp('Expr_Plus', ast.Add)
registerBinaryOp('Expr_Minus', ast.Sub)
registerBinaryOp('Expr_Mul', ast.Mult)
registerBinaryOp('Expr_Div', ast.Div)
registerBinaryOp('Expr_Mod', ast.Mod)
registerBinaryOp('Expr_ShiftLeft', ast.LShift)
registerBinaryOp('Expr_ShiftRight', ast.RShift)

registerBinaryOp('Expr_BitwiseAnd', ast.BitAnd)
registerBinaryOp('Expr_BitwiseOr', ast.BitOr)
registerBinaryOp('Expr_BitwiseXor', ast.BitXor)

registerBinaryOp('Expr_Concat', ast.Add)

registerUnaryOp('Expr_UnaryPlus', ast.UAdd)
registerUnaryOp('Expr_UnaryMinus', ast.USub)
registerUnaryOp('Expr_BooleanNot', ast.Not) # xxx: if value is int -> use invert

registerBoolOp('Expr_BooleanAnd', ast.And)
registerBoolOp('Expr_BooleanOr', ast.Or)

registerBoolOp('Expr_LogicalAnd', ast.And)
registerBoolOp('Expr_LogicalOr', ast.Or)
registerBinaryOp('Expr_LogicalXor', ast.BitXor)# todo: LogicalXor ???

registerCmpOp('Expr_Equal', ast.Eq)
registerCmpOp('Expr_Greater', ast.Gt)
registerCmpOp('Expr_GreaterOrEqual', ast.GtE)
registerCmpOp('Expr_Smaller', ast.Lt)
registerCmpOp('Expr_SmallerOrEqual', ast.LtE)
registerCmpOp('Expr_Identical', ast.Is)
registerCmpOp('Expr_NotIdentical', ast.IsNot)

def registerAugAssign(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.AugAssign(processor.process(node.var), pythonOp(), processor.process(node.expr))
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)
	
registerAugAssign('Expr_AssignPlus', ast.Add)
registerAugAssign('Expr_AssignMinus', ast.Sub)
registerAugAssign('Expr_AssignMul', ast.Mult)
registerAugAssign('Expr_AssignDiv', ast.Div)
registerAugAssign('Expr_AssignMod', ast.Mod)
registerAugAssign('Expr_AssignShiftLeft', ast.LShift)
registerAugAssign('Expr_AssignShiftRight', ast.RShift)

registerAugAssign('Expr_AssignBitwiseAnd', ast.BitAnd)
registerAugAssign('Expr_AssignBitwiseOr', ast.BitOr)
registerAugAssign('Expr_AssignBitwiseXor', ast.BitXor)

registerAugAssign('Expr_AssignConcat', ast.Add)	

@stdScope.registerTranslator
def Stmt_If(processor, node):
	ifnodes = node.elseifs[::-1] + [node]
	elsestmts = processor.process(getattr(node['else'], 'stmts', []))
	return reduce(lambda r, n: [ast.If(processor.process(n.cond), processor.process(n.stmts), r)], ifnodes, elsestmts)[0]