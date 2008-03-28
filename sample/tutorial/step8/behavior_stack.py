import stack         # import production code
from pyspec import * # import pyspec framework

class Behavior_Stack(object):
    @context(group=1)
    def new_stack(self):
        self.stack = stack.Stack()

    @spec(group=1)
    def should_be_empty(self):
        About(self.stack).should_be_empty()

    @context(group=2)
    def stack_with_one_value(self):
        self.stack = stack.Stack()
        self.stack.push(10)

    @spec(group=2)
    def should_not_be_empty(self):
        About(self.stack).should_not_be_empty()

    @spec(group=1)
    def push_should_not_return_value(self):
        About(self.stack.push(1)).should_be_none()

    @context(group=3)
    def stack_with_some_values(self):
      self.stack = stack.Stack()
      self.stack.push(10)
      self.last_value = 20
      self.stack.push(self.last_value)

    @spec(group=3)
    def should_return_last_value_by_pop_method(self):
      About(self.stack.pop()).should_equal(self.last_value)

    @context(group=4)
    def Empty_stack(self):
        self.empty_stack = stack.Stack()

    @spec(group=4, expected=stack.EmptyException)
    def should_raise_EmptyException_if_pop_called(self):
      self.empty_stack.pop()

if __name__ == "__main__":
    run_test()

