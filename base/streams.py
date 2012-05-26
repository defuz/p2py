#!/usr/bin/env python
#-*- coding:utf-8 -*-

from yaml import load_all as baseyaml
from simplejson import loads as basejson, dumps as fromjson
from cPickle import dumps as pickle, loads as frompickle
from smartdict import Dict

from utils import *

def stream(instance, cls = Dict):
	if isinstance(instance, dict):
		return cls((k, stream(v, cls)) for k,v in instance.items())
	if isinstance(instance, list):
		return [stream(i, cls) for i in instance]
	if isinstance(instance, str):
		return unicode(instance)
	return instance


def yaml(s):
	return stream(list(baseyaml(s))[0])


def json(s, cls = Dict):
	return stream(basejson(s), cls)

BASE_PATH = os.path.split(os.path.split(__file__)[0])[0] + "/"

def getFile(name, modifiers = 'r'):
	return open(os.path.join(BASE_PATH, name), modifiers)

def readFile(name):
	try:
		with open(os.path.join(BASE_PATH, name)) as f:
			return f.read()
	except Exception:
		return None

def writeFile(name, text):
	try:
		with open(os.path.join(BASE_PATH, name), 'w') as f:
			f.write(text)
	except Exception:
		return None