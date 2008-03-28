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

if __name__ == "__main__":
    run_test()

