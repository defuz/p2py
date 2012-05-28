#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast
from simply_ast import *
import copy
from translator import Scope

stdScope = Scope()



####################
# Basic constructs
####################

@stdScope.registerTranslator
def Name(processor, node):
	# Name(identifier id, expr_context ctx)
	return idnt(node.parts[0])

@stdScope.registerTranslator
def Scalar_LNumber(processor, node):
	# Num(object n)
	return ast.Num(node.value)

@stdScope.registerTranslator
def Scalar_DNumber(processor, node):
	# Num(object n)
	return ast.Num(float(node.value))

@stdScope.registerTranslator
def Scalar_String(processor, node):
	# Str(string s)
	return ast.Str(node.value)

@stdScope.registerTranslator
def Scalar_LineConst(processor, node):
	# inspect.currentframe().f_back.f_lineno
	return ast.parse('inspect.currentframe().f_back.f_lineno')

@stdScope.registerTranslator
def Scalar_FuncConst(processor, node):
	# inspect.currentframe().f_code.co_name
	return ast.parse('inspect.currentframe().f_code.co_name')

@stdScope.registerTranslator
def Scalar_FileConst(processor, node):
	# inspect.currentframe().f_code.co_filename
	return ast.parse('inspect.currentframe().f_code.co_filename')

@stdScope.registerTranslator
def Scalar_ClassConst(processor, node):
	# inspect.currentframe().f_method.im_class
	return ast.parse('inspect.currentframe().f_method.im_class')

@stdScope.registerTranslator
def Scalar_Encapsed(processor, node):
	parts = [elem.replace('%', '%%') if isinstance(elem, basestring) else '%s' for elem in node.parts]
	vars = [elem for elem in node.parts if not isinstance(elem, basestring)]
	params = ast.Tuple(processor.process(vars), []) if len(vars) > 1 else processor.process(vars[0])
	return ast.BinOp(ast.Str(''.join(parts)), ast.Mod(), params)

@stdScope.registerTranslator
def Const(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	return ast.Assign([idnt(node.name)], processor.process(node.value))

####################
# Operators
####################

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

def registerAugAssign(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.AugAssign(processor.process(node.var), pythonOp(), processor.process(node.expr))
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)

def registerAugAssignOp(phpNodeName, pythonOp):
	def translator(processor, node):
		return ast.AugAssign(processor.process(node.var), pythonOp(), ast.Num(1))
	translator.__name__ = phpNodeName
	stdScope.registerTranslator(translator)

# arithmetic ops
registerBinaryOp('Expr_Plus', ast.Add)
registerBinaryOp('Expr_Minus', ast.Sub)
registerBinaryOp('Expr_Mul', ast.Mult)
registerBinaryOp('Expr_Div', ast.Div)
registerBinaryOp('Expr_Mod', ast.Mod)

# bitwise ops
registerBinaryOp('Expr_BitwiseAnd', ast.BitAnd)
registerBinaryOp('Expr_BitwiseOr', ast.BitOr)
registerBinaryOp('Expr_BitwiseXor', ast.BitXor)
registerAugAssign('Expr_BitwiseNot', ast.Invert)
registerBinaryOp('Expr_ShiftLeft', ast.LShift)
registerBinaryOp('Expr_ShiftRight', ast.RShift)

# string ops
registerBinaryOp('Expr_Concat', ast.Add)

# unary ops
registerUnaryOp('Expr_UnaryPlus', ast.UAdd)
registerUnaryOp('Expr_UnaryMinus', ast.USub)

# boolean & logic ops
registerBoolOp('Expr_BooleanAnd', ast.And)
registerBoolOp('Expr_BooleanOr', ast.Or)

@stdScope.registerTranslator
def Expr_BooleanNot(processor, node):
	# xxx: !empty($a)
	if node.expr._ == 'Expr_Empty':
		return processor.process(node.expr.var)
	return ast.UnaryOp(ast.Not(), processor.process(node.expr))

registerBoolOp('Expr_LogicalAnd', ast.And)
registerBoolOp('Expr_LogicalOr', ast.Or)
registerBinaryOp('Expr_LogicalXor', ast.BitXor) # todo: fix this shit

# comparison ops
registerCmpOp('Expr_Equal', ast.Eq)
registerCmpOp('Expr_NotEqual', ast.NotEq)
registerCmpOp('Expr_Greater', ast.Gt)
registerCmpOp('Expr_GreaterOrEqual', ast.GtE)
registerCmpOp('Expr_Smaller', ast.Lt)
registerCmpOp('Expr_SmallerOrEqual', ast.LtE)
registerCmpOp('Expr_Identical', ast.Is)
registerCmpOp('Expr_NotIdentical', ast.IsNot)

# string assign-ops
registerAugAssign('Expr_AssignConcat', ast.Add)

# arithmetic assign-ops
registerAugAssign('Expr_AssignPlus', ast.Add)
registerAugAssign('Expr_AssignMinus', ast.Sub)
registerAugAssign('Expr_AssignMul', ast.Mult)
registerAugAssign('Expr_AssignDiv', ast.Div)
registerAugAssign('Expr_AssignMod', ast.Mod)

# bitwise assign-ops
registerAugAssign('Expr_AssignBitwiseAnd', ast.BitAnd)
registerAugAssign('Expr_AssignBitwiseOr', ast.BitOr)
registerAugAssign('Expr_AssignBitwiseXor', ast.BitXor)
registerAugAssign('Expr_AssignBitwiseNot', ast.Invert)
registerAugAssign('Expr_AssignShiftLeft', ast.LShift)
registerAugAssign('Expr_AssignShiftRight', ast.RShift)

registerAugAssignOp('Expr_PreInc', ast.Add)
registerAugAssignOp('Expr_PreDec', ast.Sub)
registerAugAssignOp('Expr_PostInc', ast.Add)
registerAugAssignOp('Expr_PostDec', ast.Sub)

####################
# Expressions
####################

@stdScope.registerTranslator
def Expr_ClassConstFetch(processor, node):
	if node['class'].parts[0] == 'self':
		return idnt(node.name)
	return attr(processor, node['class'], node.name)

@stdScope.registerTranslator
def Expr_PropertyFetch(processor, node):
	return attr(processor, node.var, node.name)

@stdScope.registerTranslator
def Expr_ConstFetch(processor, node):
	return processor.process(node.name)

@stdScope.registerTranslator
def Expr_Variable(processor, node):
	return idnt(node.name)

@stdScope.registerTranslator
def Expr_Assign(processor, node):
	# xxx: $a[] = 42
	if node.var._ == 'Expr_ArrayDimFetch' and node.var.dim is None:
		return call(attr(processor, node.var.var, 'append'), [processor.process(node.expr)])
	# todo: $this->$name = $value as setattr
	return ast.Assign([processor.process(node.var)], processor.process(node.expr))

@stdScope.registerTranslator
def Expr_AssignRef(processor, node):
	return Expr_Assign(processor, node) # todo: make the difference

@stdScope.registerTranslator
def Expr_Isset(processor, node):
	# todo: use context for isset!
	# Compare(expr left, cmpop* ops, expr* comparators)
	return ast.Compare(processor.process(node.vars[0]), [ast.IsNot()], [idnt('None')])

@stdScope.registerTranslator
def Expr_Ternary(processor, node):
	# IfExp(expr test, expr body, expr orelse)
	return ast.IfExp(processor.process(node.cond), processor.process(node['if']), processor.process(node['else']))

@stdScope.registerTranslator
def Expr_StaticPropertyFetch(processor, node):
	# Attribute(expr value, identifier attr, expr_context ctx)
	if node['class'].parts[0] == 'self':
		return idnt(node.name)
	return attr(processor, node['class'], node.name)

@stdScope.registerTranslator
def Expr_ArrayDimFetch(processor, node):
	# Subscript(expr value, slice slice, expr_context ctx)
	return ast.Subscript(processor.process(node.var), processor.process(node.dim), [])

@stdScope.registerTranslator
def Arg(processor, node):
	return processor.process(node.value)

@stdScope.registerTranslator
def Expr_FuncCall(processor, node):
	return call(processor.process(node.name), processor.process(node.args))

@stdScope.registerTranslator
def Expr_MethodCall(processor, node):
	name = node.name if isinstance(node.name, basestring) else '$$$'
	return call(attr(processor, node.var, name), processor.process(node.args))

@stdScope.registerTranslator
def Expr_StaticCall(processor, node):
	if node['class'].parts[0] == 'self':
		return call(idnt(node.name), processor.process(node.args))
	return call(attr(processor, node['class'], node.name), processor.process(node.args))

@stdScope.registerTranslator
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

@stdScope.registerTranslator
def Expr_Empty(processor, node):
	return ast.UnaryOp(ast.Not(), processor.process(node.var))

@stdScope.registerTranslator
def Expr_New(processor, node):
	# Call(expr func, expr* args, keyword* keywords,expr? starargs, expr? kwargs)
	return call(processor.process(node['class']), processor.process(node.args))

@stdScope.registerTranslator
def Expr_Instanceof(processor, node):
	# Call(expr func, expr* args, keyword* keywords,expr? starargs, expr? kwargs)
	return call(idnt('isinstance'), [processor.process(node.expr)] + [processor.process(node['class'])])

@stdScope.registerTranslator
def Expr_ErrorSuppress(processor, node):
	# TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
	# ExceptHandler(expr? type, expr? name, stmt* body)
	return ast.TryExcept([processor.process(node.expr)], [ast.ExceptHandler(idnt('BaseException'), None, [ast.Pass()])], [])

#### casts ####

@stdScope.registerTranslator
def Expr_Cast_Int(processor, node):
	return call(idnt('int'), [processor.process(node.expr)])

@stdScope.registerTranslator
def Expr_Cast_Double(processor, node):
	return call(idnt('float'), [processor.process(node.expr)])

# todo: implement other casts

####################
# Statements
####################

@stdScope.registerTranslator
def Stmt_Class(processor, node):
	# ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
	extends = [processor.process(node.extends)] if node.extends else [idnt('object')]
	stmts = processor.process(node.stmts) if node.stmts else ast.Pass()
	return ast.ClassDef(node.name, extends, stmts, [])

@stdScope.registerTranslator
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

@stdScope.registerTranslator
def Stmt_Return(processor, node):
	return ast.Return(processor.process(node.expr) if node.expr else None)

@stdScope.registerTranslator
def Stmt_ClassConst(processor, node):
	return processor.process(node.consts)[0]

@stdScope.registerTranslator
def Stmt_PropertyProperty(processor, node):
	# Assign(expr* targets, expr value)
	# Name(identifier id, expr_context ctx)
	# xxx: class property without default value
	if node.default:
		return ast.Assign([idnt(node.name)], processor.process(node.default))
	else:
		return str('# ' + node.name)

@stdScope.registerTranslator
def Stmt_Property(processor, node):
	return processor.process(node.props)[0]

@stdScope.registerTranslator
def Stmt_Echo(processor, node):
	return ast.Print(None, processor.process(node.exprs), True)

@stdScope.registerTranslator
def Stmt_If(processor, node):
	# If(expr test, stmt* body, stmt* orelse)
	ifnodes = node.elseifs[::-1] + [node]
	elsestmts = processor.process(getattr(node['else'], 'stmts', []))
	return reduce(lambda r, n: [ast.If(processor.process(n.cond), processor.process(n.stmts), r)], ifnodes, elsestmts)[0]


@stdScope.registerTranslator
def Stmt_Foreach(processor, node):
	if not node.keyVar:
		return ast.For(processor.process(node.valueVar), processor.process(node.expr), processor.process(node.stmts), None)
	# todo: enumerate(expr) or expr.items() ?
	target = ast.Tuple(processor.process([node.keyVar,node.valueVar]), [])
	expr = call(attr(processor, node.expr, 'items'), [])
	return ast.For(target, expr, processor.process(node.stmts), None)

@stdScope.registerTranslator
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

@stdScope.registerTranslator
def Stmt_For(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	loop = ast.While(
		processor.process(node.cond)[0] if node.cond else idnt('True'),
		processor.process(node.stmts) + processor.process(node.loop),
		[]
	)
	return processor.process(node.init) + [loop] if node.init else loop

@stdScope.registerTranslator
def Stmt_While(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	return ast.While(processor.process(node.cond), processor.process(node.stmts), [])

@stdScope.registerTranslator
def Stmt_Do(processor, node):
	# While(expr test, stmt* body, stmt* orelse)
	# If(expr test, stmt* body, stmt* orelse)
	return ast.While(idnt('True'), processor.process(node.stmts) + [ast.If(
		ast.UnaryOp(ast.Not(), processor.process(node.cond)), [ast.Break()], []
	)], [])

@stdScope.registerTranslator
def Stmt_Break(processor, node):
	if node.num and node.num > 1:
		raise NotImplementedError("Couldn't break more than one loop")
	return ast.Break()

@stdScope.registerTranslator
def Stmt_Continue(processor, node):
	if node.num and node.num > 1:
		raise NotImplementedError("Couldn't continue more than one loop")
	return ast.Continue()

@stdScope.registerTranslator
def Stmt_Throw(processor, node):
	# Raise(expr? type, expr? inst, expr? tback)
	return ast.Raise(processor.process(node.expr), None, None)

@stdScope.registerTranslator
def Stmt_TryCatch(processor, node):
	# TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
	# ExceptHandler(expr? type, expr? name, stmt* body)
	return ast.TryExcept(processor.process(node.stmts), map(lambda catch: ast.ExceptHandler(
		processor.process(catch.type), idnt(catch.var), processor.process(catch.stmts)
	), node.catches), [])

@stdScope.registerTranslator
def Stmt_Unset(processor, node):
	# todo: unset($this->$name) as delattr
	return ast.Delete(processor.process(node.vars))