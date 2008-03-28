# -*- coding: ascii -*-

# I refered TDD:Test Driven Develpment by Example(Kent Beck).
# I changed that test style to use data provider

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *


def fibonacci(n):
    if n == 0:
        return 0
    if n <= 2:
        return 1
    return fibonacci(n-1) + fibonacci(n-2)


class Behavior_fibonacci(object):
    @classmethod
    @data_provider(key=("n", "expected_return"))
    def create_data_for_test(cls):
        return ((0, 0), (1, 1), (2, 1), (3, 2))

    @spec
    def fibonacci_should_return_expected_value(self, n, expected_return):
        About(fibonacci(n)).should_equal(expected_return)


if __name__ == "__main__":
    run_test()
