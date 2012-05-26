#!/usr/bin/env python
#-*- coding:utf-8 -*-

def validDictProperty(name, value):
	return not name.startswith("__") and not callable(value) and not isinstance(value, (property, classmethod, staticmethod))


class DictMetaclass(type):
	def __init__(cls, name, bases, namespace):
		cls.default = {}
		for base in bases:
			if hasattr(base, "default"):
				cls.default.update(base.default)
		cls.default.update((name, value) for name, value in namespace.items() if validDictProperty(name, value))

	def configurate(cls, configs):
		cls.default.update(configs)


class Dict(dict):
	__metaclass__ = DictMetaclass

	def __new__(cls, *args, **kwargs):
		self = dict.__new__(cls)
		self.update(cls.default)
		self.__dict__ = self
		return self

	def __hash__(self): return id(self)

	def repr(self):
		return ', '.join(key + "=" + str(value) for key, value in self.items())