# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework
import pyspec.reloader as reloader
import socket


class data_provider_Behavior(object):
    class data_provider_Fixture(object):
        mock = None

        @context
        def context(self):
            if self.mock is not None:
                self.mock.context()

        @classmethod
        @data_provider(key="i")
        def generate_1_to_3(cls):
            print "data_provider*************:"
            if cls.mock is not None:
                cls.mock.data_provider()
            return range(1, 4)

        @spec
        def spec(self, i):
            if self.mock is not None:
                self.mock.spec(i)

    @context(group=1)
    def A_test_trigger_with_data_provider(self):
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)
        try:
            self.trigger.run()
        except TypeError:
            pass

    @spec(group=1)
    def should_regist_data_provider(self):
        About(len(self.trigger.data_providers)).should_equal(1)

    @context(group=2)
    def A_data_provider(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.data_provider()
        recorder.context()
        recorder.spec(1)
        recorder.context()
        recorder.spec(2)
        recorder.context()
        recorder.spec(3)
        self.data_provider_Fixture.mock = recorder._get_mock_object_()
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=2)
    def should_be_called(self):
        self.trigger.run()
        self.data_provider_Fixture.mock._verify_()


class multi_data_provider_Behavior(object):
    class data_provider_Fixture(object):
        mock = None

        @context
        def context(self):
            if self.mock is not None:
                self.mock.context()

        @classmethod
        @data_provider(key="i")
        def generate_1_to_2(cls):
            print "data_provider*************:"
            if cls.mock is not None:
                cls.mock.data_provider_1()
            return range(1, 3)

        @classmethod
        @data_provider(key="j")
        def generate_3_to_4(cls):
            print "data_provider*************:"
            if cls.mock is not None:
                cls.mock.data_provider_2()
            return range(3, 5)

        @spec
        def spec(self, i, j):
            if self.mock is not None:
                self.mock.spec(i, j)

    @context(group=1)
    def _direct_product_test_data__(self):
        data = [("key1", [1, 2]), ("key2", [3, 4])]
        self.arg_list = pyspec.framework._direct_product_test_data(data)

    @spec(group=1)
    def should_create_data_conbination(self):
        About(len(self.arg_list)).should_equal(4)
        About(self.arg_list[0]["key1"]).should_equal(1)
        About(self.arg_list[0]["key2"]).should_equal(3)

    @context(group=2)
    def A_test_trigger_with_2_multi_data_providers(self):
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)
        try:
            self.trigger.run()
        except TypeError:
            pass

    @spec(group=2)
    def should_regist_data_providers(self):
        About(len(self.trigger.data_providers)).should_equal(2)

    @context(group=3)
    def A_multi_data_provider(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.data_provider_1()
        recorder.data_provider_2()
        recorder.context()
        recorder.spec(1, 3)
        recorder.context()
        recorder.spec(2, 3)
        recorder.context()
        recorder.spec(1, 4)
        recorder.context()
        recorder.spec(2, 4)
        self.data_provider_Fixture.mock = recorder._get_mock_object_()
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=3)
    def should_be_called(self):
        self.trigger.run()
        self.data_provider_Fixture.mock._verify_()


class multi_key_data_provider_Behavior(object):
    class data_provider_Fixture(object):
        mock = None

        @context
        def context(self):
            self.mock.context()

        @classmethod
        @data_provider(key=("i", "j"))
        def generate_pair_data(cls):
            print "data_provider*************:"
            if cls.mock is not None:
                cls.mock.data_provider_1()
            return [(1, 2), (3, 4)]

        @classmethod
        @data_provider(key="k")
        def generate_5_to_6(cls):
            print "data_provider*************:"
            if cls.mock is not None:
                cls.mock.data_provider_2()
            return range(5, 7)

        @spec
        def spec(self, i, j, k):
            if self.mock is not None:
                self.mock.spec(i, j, k)

    @context(group=1)
    def _direct_product_test_data__with_multi_key_data(self):
        data = [(("key1", "key2"), [(1, 2), (3, 4)]), ("key3", [5, 6])]
        self.arg_list = pyspec.framework._direct_product_test_data(data)
        #print self.arg_list

    @spec(group=1)
    def create_multi_key_data_conbination(self):
        About(len(self.arg_list)).should_equal(4)
        About(self.arg_list[0]["key1"]).should_equal(1)
        About(self.arg_list[0]["key2"]).should_equal(2)
        About(self.arg_list[0]["key3"]).should_equal(5)

    @context(group=2)
    def _direct_product_test_data__with_args_which_have_different_length(self):
        self.data = [(("key1", "key2"), [(1, 2), (3,)]), ("key3", [5, 6])]


    @spec(group=2, expected=ValueError)
    def should_fail(self):
        arg_list = pyspec.framework._direct_product_test_data(self.data)

    @context(group=3)
    def A_test_trigger_with_2_multi_key_data_providers(self):
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)
        try:
            self.trigger.run()
        except TypeError:
            pass

    @spec(group=3)
    def should_regist_data_providers(self):
        About(len(self.trigger.data_providers)).should_equal(2)

    @context(group=4)
    def A_multi_key_data_provider(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.data_provider_1()
        recorder.data_provider_2()
        recorder.context()
        recorder.spec(1, 2, 5)
        recorder.context()
        recorder.spec(3, 4, 5)
        recorder.context()
        recorder.spec(1, 2, 6)
        recorder.context()
        recorder.spec(3, 4, 6)
        self.data_provider_Fixture.mock = recorder._get_mock_object_()
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=4)
    def should_be_called(self):
        self.trigger.run()
        self.data_provider_Fixture.mock._verify_()


class data_provider_grouping_Behavior(object):
    class data_provider_Fixture(object):
        mock = None

        @context
        def context(self):
            self.mock.context()

        @classmethod
        @data_provider(key="i", group=1)
        def generate_1_to_2(cls):
            print "data_provider*************:"
            cls.mock.data_provider_1()
            return range(1, 3)

        @classmethod
        @data_provider(key="j", group=2)
        def generate_3_to_4(cls):
            print "data_provider*************:"
            cls.mock.data_provider_2()
            return range(3, 5)

        @spec(group=1)
        def spec1(self, i):
            self.mock.spec1(i)

        @spec(group=2)
        def spec2(self, j):
            self.mock.spec2(j)

    @context
    def A_data_providers_with_group(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.data_provider_1()
        recorder.spec1(1)
        recorder.spec1(2)
        recorder.data_provider_2()
        recorder.spec2(3)
        recorder.spec2(4)
        self.data_provider_Fixture.mock = recorder._get_mock_object_()
        fixture = self.data_provider_Fixture()
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec
    def should_be_called_in_same_group_spec(self):
        self.trigger.run()
        self.data_provider_Fixture.mock._verify_()


class BugReemergenceTest20080203(object):
    @context(group=1)
    def A_bug_about_multi_key_data_provider(self):
        data = [(("n", "expected_return"), [(0, 0), (1, 1), (2, 1), (3, 2)],)]
        self.arg_list = pyspec.framework._direct_product_test_data(data)

    @spec(group=1)
    def should_be_repaired(self):
        About(len(self.arg_list)).should_equal(4)

    class BugReemergenceFixture(object):
        def __init__(self, mock):
            self.mock = mock

        @classmethod
        @data_provider(key=("n", "expected_return"))
        def create_data_for_test(self):
            return ((0, 0), (1, 1), (2, 1), (3, 2))

        @spec
        def record_test_input(self, n, expected_return):
            self.mock.record_test_input(n, expected_return)

    @context(group=2)
    def A_bug_about_multi_key_data_provider2(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.record_test_input(0, 0)
        recorder.record_test_input(1, 1)
        recorder.record_test_input(2, 1)
        recorder.record_test_input(3, 2)
        self.mock = recorder._get_mock_object_()
        fixture = self.BugReemergenceFixture(self.mock)
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=2)
    def should_be_repaired2(self):
        self.trigger.run()
        self.mock._verify_()


if __name__ == "__main__":
    run_test()
