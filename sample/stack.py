# -*- coding: utf_8 -*-

class Stack(object):
	def __init__(self):
		self.item = None

	def __len__(self):
		if self.item is None:
			return 0
		return 1

	def push(self, item):
		self.item = item

	def top(self):
		return self.item
