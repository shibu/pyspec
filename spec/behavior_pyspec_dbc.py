# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.embedded.dbc import *
from pyspec.mockobject import *

class Behavior_DesignByContract_PrePost(object):
    class Counter(DbCobject):
        def __init__(self, mock):
            super(Behavior_DesignByContract_PrePost.Counter, self).__init__()
            self.value = 0
            self.mock = mock

        @DbC
        def count__pre(self, value):
            self.mock.pre_condition()
            About(value < 20).should_be_true()
            About(value > 0).should_be_true()

        def count(self, value):
            self.mock.method_call()
            self.value += value
            return self.value

        @DbC
        def count__post(self, ret_value):
            self.mock.post_condition()
            About(isinstance(ret_value, int)).should_be_true()
            About(ret_value > 0).should_be_true()

    @context(group=1)
    def Pre_and_post_conditions(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.pre_condition()
        recorder.method_call()
        recorder.post_condition()
        self.mock = recorder._get_mock_object_()
        self.a_counter = self.Counter(self.mock)

    @context(group=2)
    def Dbc_option_on(self):
        set_dbc_option(prepost=True)

    @spec(group=[1, 2], dbc=False)
    def should_be_checked_by_dbc_rules(self):
        About(self.a_counter.count(1)).should_equal(1)
        self.mock._verify_()

    @spec(group=1)
    def should_be_checked_by_dbc_rules_automatically_in_pyspec(self):
        About(self.a_counter.count(1)).should_equal(1)
        self.mock._verify_()

    @context(group=3)
    def Pre_and_post_conditions2(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.method_call()
        self.mock = recorder._get_mock_object_()
        self.a_counter = self.Counter(self.mock)

    @spec(group=3, dbc=False)
    def should_not_be_checked_if_dbc_option_is_turned_off(self):
        About(self.a_counter.count(1)).should_equal(1)
        self.mock._verify_()


class Behavior_DesignByContract_Invariant(object):
    class Counter(DbCobject):
        def __init__(self, mock):
            super(Behavior_DesignByContract_Invariant.Counter, self).__init__()
            self.value = 0
            self.mock = mock

        @DbC
        def __invariant(self):
            self.mock.invariant()
            About(self.value < 20).should_be_true()
            About(self.value > 0).should_be_true()

        def count(self, value):
            self.mock.method_call()
            self.value += value
            return self.value

    @context
    def A_invariant_method(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.method_call()
        recorder.invariant()
        self.mock = recorder._get_mock_object_()
        self.a_counter = self.Counter(self.mock)
        set_dbc_option(invariant=True)

    @spec(dbc=False)
    def should_be_checked_by_dbc_rules(self):
        About(self.a_counter.count(1)).should_equal(1)
        self.mock._verify_()


if __name__ == "__main__":
    run_test()

