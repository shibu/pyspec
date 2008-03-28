# -*- coding: utf_8 -*-

from pyspec import *
from stack import *

class StackBehavior(object):
	"""スタックの動作仕様."""
	@context(group=0)
	def New_stack(self):
		"""新しいスタック."""
		self.stack = Stack()

	@spec(group=0)
	def should_empty(self):
		"""空でなければならない."""
		About(self.stack).should_be_empty()

	@spec(group=0)
	def should_not_be_empty_after_push(self):
		"""push()後は空ではない"""
		self.stack.push(37)
		About(self.stack).should_not_be_empty()

	@context(group=1)
	def A_stack_with_one_item(self):
		"""要素をひとつ持つスタック."""
		self.stack = Stack()
		self.stack.push("one item")

	@spec(group=1)
	def should_return_top_when_top_method_called(self):
		"""top()メソッドを呼ぶと、先頭の要素を返す."""
		About(self.stack.top()).should_equal("one item")

	@spec(group=1)
	def should_not_be_empty(self):
		"""空ではない."""
		print "コンソールに出した文字列が表示されます"
		About(self.stack).should_not_be_empty()

if __name__ == "__main__":
    run_test()
