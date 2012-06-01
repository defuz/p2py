#!/usr/bin/env python
#-*- coding:utf-8 -*-

from simply_ast import *
from scope import syntax

def registerBinaryOp(pythonOp):
	return syntax(lambda processor, node: ast.BinOp(processor.process(node.left), pythonOp(), processor.process(node.right)))

def registerBoolOp(pythonOp):
	return syntax(lambda processor, node: ast.BoolOp(pythonOp(), [processor.process(node.left), processor.process(node.right)]))

def registerUnaryOp(pythonOp):
	return syntax(lambda processor, node: ast.UnaryOp(pythonOp(), processor.process(node.expr)))

def registerCmpOp(pythonOp):
	return syntax(lambda processor, node: ast.Compare(processor.process(node.left), [pythonOp()], [processor.process(node.right)]))

def registerAugAssign(pythonOp):
	return syntax(lambda processor, node: ast.AugAssign(processor.process(node.var), pythonOp(), processor.process(node.expr)))

def registerAugAssignOp(pythonOp):
	return syntax(lambda processor, node: ast.AugAssign(processor.process(node.var), pythonOp(), ast.Num(1)))

# arithmetic ops
Expr_Plus = registerBinaryOp(ast.Add)
Expr_Minus = registerBinaryOp(ast.Sub)
Expr_Mul = registerBinaryOp(ast.Mult)
Expr_Div = registerBinaryOp(ast.Div)
Expr_Mod = registerBinaryOp(ast.Mod)

# bitwise ops
Expr_BitwiseAnd = registerBinaryOp(ast.BitAnd)
Expr_BitwiseOr = registerBinaryOp(ast.BitOr)
Expr_BitwiseXor = registerBinaryOp(ast.BitXor)
Expr_BitwiseNot = registerAugAssign(ast.Invert)
Expr_ShiftLeft = registerBinaryOp(ast.LShift)
Expr_ShiftRight = registerBinaryOp(ast.RShift)

# string ops
Expr_Concat = registerBinaryOp(ast.Add)

# unary ops
Expr_UnaryPlus = registerUnaryOp(ast.UAdd)
Expr_UnaryMinus = registerUnaryOp(ast.USub)

# boolean & logic ops
Expr_BooleanAnd = registerBoolOp(ast.And)
Expr_BooleanOr = registerBoolOp(ast.Or)

@syntax
def Expr_BooleanNot(processor, node):
	# xxx: !empty($a)
	if node.expr._ == 'Expr_Empty':
		return processor.process(node.expr.var)
	return ast.UnaryOp(ast.Not(), processor.process(node.expr))

Expr_LogicalAnd = registerBoolOp(ast.And)
Expr_LogicalOr = registerBoolOp(ast.Or)
Expr_LogicalXor = registerBinaryOp(ast.BitXor) # todo: fix this shit

# comparison ops
Expr_Equal = registerCmpOp(ast.Eq)
Expr_NotEqual = registerCmpOp(ast.NotEq)
Expr_Greater = registerCmpOp(ast.Gt)
Expr_GreaterOrEqual = registerCmpOp(ast.GtE)
Expr_Smaller = registerCmpOp(ast.Lt)
Expr_SmallerOrEqual = registerCmpOp(ast.LtE)
Expr_Identical = registerCmpOp(ast.Is)
Expr_NotIdentical = registerCmpOp(ast.IsNot)

# string assign-ops
Expr_AssignConcat = registerAugAssign(ast.Add)

# arithmetic assign-ops
Expr_AssignPlus = registerAugAssign(ast.Add)
Expr_AssignMinus = registerAugAssign(ast.Sub)
Expr_AssignMul = registerAugAssign(ast.Mult)
Expr_AssignDiv = registerAugAssign(ast.Div)
Expr_AssignMod = registerAugAssign(ast.Mod)

# bitwise assign-ops
Expr_AssignBitwiseAnd = registerAugAssign(ast.BitAnd)
Expr_AssignBitwiseOr = registerAugAssign(ast.BitOr)
Expr_AssignBitwiseXor = registerAugAssign(ast.BitXor)
Expr_AssignBitwiseNot = registerAugAssign(ast.Invert)
Expr_AssignShiftLeft = registerAugAssign(ast.LShift)
Expr_AssignShiftRight = registerAugAssign(ast.RShift)

Expr_PreInc = registerAugAssignOp(ast.Add)
Expr_PreDec = registerAugAssignOp(ast.Sub)
Expr_PostInc = registerAugAssignOp(ast.Add)
Expr_PostDec = registerAugAssignOp(ast.Sub)
