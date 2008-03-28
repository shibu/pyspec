# -*- coding: utf_8 -*-

from pyspec import *
from stack import *

class Stack_Behavior(object):
	@context(group=0)
	def New_stack(self):
		self.stack = Stack()

	@spec(group=0)
	def should_empty(self):
		About(self.stack).should_be_empty()

	@spec(group=0)
	def should_not_be_empty_after_push(self):
		self.stack.push(37)
		About(self.stack).should_not_be_empty()

	@context(group=1)
	def A_stack_with_one_item(self):
		self.stack = Stack()
		self.stack.push("one item")

	@spec(group=1)
	def should_return_top_when_top_method_called(self):
		About(self.stack.top()).should_equal("one item")

	@spec(group=1)
	def should_not_be_empty(self):
		print "you can see the text that was written in console."
		About(self.stack).should_not_be_empty()

if __name__ == "__main__":
    run_test()
