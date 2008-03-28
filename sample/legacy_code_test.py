# -*- coding: ascii -*-

"""This sample shows the test for legacy code that has no test.

If you wrote spec that used should_not_be_changed(),
when you extend or refactor the legacy program.
"""

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *


class AddressBook(object):
    """This class has no test."""
    def __init__(self):
        self.address_list = {"Taro":"Tokyo", "Jiro":"Osaka"}

    def home(self, name):
        return self.address_list[name]


class Behavior_AddressBook(object):
    @context
    def a_address_book(self):
        self.address_book = AddressBook()

    @spec
    def should_have_home_of_taro(self):
        About(self.address_book.home("Taro")).should_not_be_changed()

    @spec
    def should_have_home_of_jiro(self):
        About(self.address_book.home("Jiro")).should_not_be_changed(reset=True)


if __name__ == "__main__":
    run_test()
