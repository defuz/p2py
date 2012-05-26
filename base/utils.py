#!/usr/bin/env python
#-*- coding:utf-8 -*-

#!/usr/bin/env python
#-*- coding:utf-8 -*-

from functools import reduce, update_wrapper
from functools import partial as carry
import itertools, logging, os, sys

class Singleton(type):
	instance = None

	def __call__(cls, *args, **kwargs):
		if not cls.instance:
			cls.instance = cls.__new__(cls, *args, **kwargs)
		cls.__init__(cls.instance, *args, **kwargs)
		return cls.instance


class lazyobject(object):
	def __getattr__(self, name):
		attr = self.__lazyattr__(name)
		setattr(self, name, attr)
		return attr

	def __setattr__(self, name, value):
		raise NotImplementedError()

def funcCallRepr(func, args=None, kwargs=None):
	args = ', '.join(map(repr, args)) if args else None
	kwargs = ', '.join(name + "=" + repr(value) for name, value in kwargs.items()) if kwargs else None
	return "%s(%s)" % (func.__name__, ', '.join(filter(None, [args, kwargs])))

def funcDebug(func):
	log = logging.getLogger(func.__module__)
	def wrapper(*args, **kwags):
		log.debug(funcCallRepr(func, args, kwags))
		return func(*args, **kwags)
	update_wrapper(wrapper, func)
	return wrapper
