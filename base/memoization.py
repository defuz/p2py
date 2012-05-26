#!/usr/bin/env python
#-*- coding:utf-8 -*-

from utils import *

def memoized(func):
	cache = {}

	def wrapper(*args):
		if args not in cache:
			cache[args] = func(*args)
		return cache[args]

	update_wrapper(wrapper, func)
	return wrapper


def memoizedProperty(fget, name=None):
	if name is None:
		name = fget.__name__

	def getter(self):
		if name not in self.__dict__:
			value = self.__dict__[name] = fget(self)
			return value
		return self.__dict__[name]

	update_wrapper(getter, fget)
	return property(getter)


def memoizedMethod(method, name=None):
	if name is None:
		name = method.__name__

	def wrapper(self, *args):
		cache = self.__dict__.setdefault("__" + name, {})
		try:
			return cache[args]
		except KeyError:
			value = method(self, *args)
			cache[args] = value
			return value

	update_wrapper(wrapper, method)
	return wrapper