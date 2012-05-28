#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ast

def idnt(s):
	if s == 'this':
		s = 'self'
	return ast.Name(s, [])

def call(func, args):
	return ast.Call(func, args, [], None, None)

def attr(processor, var, name):
	if isinstance(name, basestring):
		return ast.Attribute(processor.process(var), name, [])
	return call(idnt('getattr'), [processor.process(var), processor.process(name)])