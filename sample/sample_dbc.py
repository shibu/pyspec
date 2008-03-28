# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.embedded import *
from pyspec.embedded.dbc import *


class Weight(DbCobject):
    convert_table = {"kg":1.0, "kan":3.75, "pound":0.45359237}

    def __init__(self, unit, value):
        super(Weight, self).__init__()
        self.set_unit(unit)
        self.value = value

    @DbC
    def set_unit__pre(self, unit):
        About(unit in self.convert_table).should_be_true()

    def set_unit(self, unit):
        self.unit = unit

    @classmethod
    def kan(cls, value):
        return cls("kan", value)

    @classmethod
    def pound(cls, value):
        return cls("pound", value)

    def to_Kg(self):
        return self.value * self.convert_table[self.unit]

    def to_kan(self):
        return self.value * self.convert_table[self.unit] / \
                            self.convert_table["kan"]

    def to_pound(self):
        return self.value * self.convert_table[self.unit] / \
                            self.convert_table["pound"]

    def _convert_to(self, unit):
        convert_method = {"kg":self.to_Kg, "kan":self.to_kan,
                        "pound":self.to_pound}
        return convert_method[unit]()

    def __add__(self, another):
        return Weight(self.unit, self.value + another._convert_to(self.unit))


def test_main():
    """Use DbC support without PySpec"""
    set_dbc_option(prepost=True)
    total = Weight.pound(100) + Weight.kan(100)
    weight = Weight("momme", 100) # Error: unsupport Japanese unit


class Behavior_Weight(object):
    """DbC support in PySpec"""
    @context(group=1)
    def JapaneseWeight(self):
        self.kan = Weight.kan(10)

    @spec(group=1)
    def can_convert_to_Kg(self):
        About(self.kan.to_Kg()).should_equal_nearly(37.5)

    @context(group=2)
    def Pound(self):
        self.pound = Weight.pound(10)

    @spec(group=2)
    def can_convert_to_kan(self):
        About(self.pound.to_kan()).should_equal_nearly(0.4536 * 10 / 3.75)

    @context(group=3)
    def Momme(self):
        self.momme = Weight("momme", 100) # Error: momme is not supported!

    @spec(group=3)
    def can_convert_pound(self):
        About(self.momme.to_pound()).should_equal_nearly(0.00375 * 100 / 0.453)


if __name__ == "__main__":
    if "--run-itself" in sys.argv:
        test_main()
    elif "--run-on-pyspec" in sys.argv:
        sys.argv.remove("--run-on-pyspec")
        run_test()
    else:
        print """$ dbc_example [option]
    --run-itself
    --run-on-pyspec
"""
