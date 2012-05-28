#!/usr/bin/env python
#-*- coding:utf-8 -*-

from progressbar import ProgressBar

def progress(query, count = None):
	if count is None:
		query = tuple(query)
		count = len(query)
	if not count:
		raise StopIteration
	progressbar = ProgressBar(maxval=count)
	progressbar.start()
	for i, el in enumerate(query):
		yield el
		progressbar.update(i+1)
