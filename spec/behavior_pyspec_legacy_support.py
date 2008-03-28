# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework
import pyspec.embedded.setting as setting
from pyspec.legacycode import test_proxy


class Behavior_should_not_be_changed():
    @context(group=1)
    def recording_key_generator_was_called_once(self):
        config = setting.PySpecConfig()
        self.module_name = "TestModule"
        self.class_name = "Behavior_Something"
        self.method_name = "XXX_should_do"
        self.variable_name = "test_data"
        config.runtime.module_name = self.module_name
        config.runtime.class_name = self.class_name
        config.runtime.method_name = self.method_name
        self.result = config.runtime._recording_key(self.variable_name)
        self.expected_index = 0

    @spec(group=1)
    def should_return_unique_key_with_index_0(self):
        About(self.result[0]).should_equal(self.module_name)
        About(self.result[1]).should_equal(self.class_name)
        About(self.result[2]).should_equal(self.method_name)
        About(self.result[3]).should_equal(self.variable_name)
        About(self.result[4]).should_equal(self.expected_index)

    @context(group=2)
    def recording_key_generator_was_called_twice_with_same_variable_name(self):
        config = setting.PySpecConfig()
        self.first_result = config.runtime._recording_key("test_data")
        self.second_result = config.runtime._recording_key("test_data")

    @spec(group=2)
    def should_return_unique_keys(self):
        About(self.first_result).should_not_equal(self.second_result)

    @context(group=3)
    def reference_key_was_called_twice_with_same_variable_name(self):
        config = setting.PySpecConfig()
        self.first_result = config.runtime._reference_key("test_data")
        self.second_result = config.runtime._reference_key("test_data")

    @spec(group=3)
    def should_return_same_keys(self):
        About(self.first_result).should_equal(self.second_result)

    @context(group=4)
    def legacy_record_without_record(self):
        self.config = setting.PySpecConfig()
        self.key = config.runtime._reference_key("legacy_data")

    @spec(group=4)
    def should_not_have_key(self):
        About(self.config.runtime._has_key(self.key)).should_be_false()

    @context(group=5)
    def legacy_record_was_recorded(self):
        self.config = setting.PySpecConfig()
        self.key = self.config.runtime._reference_key("legacy_data")
        self.expectec_value = 10
        self.value, self.is_changed = self.config.runtime.get_recorded_value(
                "legacy_data", self.expectec_value)

    @spec(group=5)
    def should_have_a_key(self):
        About(self.config.runtime._has_key(self.key)).should_be_true()

    @spec(group=5)
    def recorded_value_should_be_return(self):
        About(self.value).should_equal(self.expectec_value)

    @spec(group=5)
    def changed_flag_should_be_turned_on(self):
        About(self.is_changed).should_be_true()

    @context(group=6)
    def legacy_record_was_recorded_at_past_time(self):
        self.config = setting.PySpecConfig()
        self.key = self.config.runtime._reference_key("legacy_data")
        self.expected_value = 10
        self.config.runtime.get_recorded_value("legacy_data",
                self.expected_value)
        self.config.runtime.start_spec() # reset index
        self.value, self.is_changed = self.config.runtime.get_recorded_value(
                "legacy_data", 20)

    @spec(group=6)
    def should_have_a_key2(self):
        About(self.config.runtime._has_key(self.key)).should_be_true()

    @spec(group=6)
    def recorded_old_value_should_be_returned(self):
        About(self.value).should_equal(self.expected_value)

    @spec(group=6)
    def changed_flag_should_not_be_turned_on(self):
        About(self.is_changed).should_be_false()

    @context(group=7)
    def legacy_record_was_recorded_at_past_time_and_reset_flag_on(self):
        self.config = setting.PySpecConfig()
        self.key = self.config.runtime._reference_key("legacy_data")
        self.config.runtime.get_recorded_value("legacy_data", 10)
        self.config.runtime.start_spec() # reset index
        self.expected_value = 20
        self.value, self.is_changed = self.config.runtime.get_recorded_value(
                "legacy_data", self.expected_value, reset=True)

    @spec(group=7)
    def should_have_a_key3(self):
        About(self.config.runtime._has_key(self.key)).should_be_true()

    @spec(group=7)
    def should_return_recorded_value2(self):
        About(self.value).should_equal(self.expected_value)

    @spec(group=7)
    def should_have_recording_flag2(self):
        About(self.is_changed).should_be_true()

    class LegacySupportFixture(object):
        def __init__(self, value):
            self.value = value

        @spec
        def get_values(self):
            About(self.value).should_not_be_changed()

    @context(group=8)
    def the_value_does_not_changed_in__should_not_be_changed__(self):
        self.config = setting.PySpecConfig()
        self.fixture1 = self.LegacySupportFixture(10)
        self.fixture2 = self.LegacySupportFixture(10)

    @spec(group=8)
    def should_not_fail(self):
        self.config.runtime.start_spec()
        trigger1 = pyspec.framework.SpecTestTrigger(self.fixture1,
                runtime_option=self.config.runtime)
        trigger1.run()
        self.config.runtime.start_spec()
        trigger2 = pyspec.framework.SpecTestTrigger(self.fixture2,
                runtime_option=self.config.runtime)
        trigger2.run()

    @context(group=9)
    def the_value_changed_in__should_not_be_changed__(self):
        self.config = setting.PySpecConfig()
        self.fixture1 = self.LegacySupportFixture(10)
        self.fixture2 = self.LegacySupportFixture(20)

    @spec(expected=AssertionError, group=9)
    def should_fail(self):
        self.config.runtime.start_spec()
        trigger1 = pyspec.framework.SpecTestTrigger(self.fixture1,
                runtime_option=self.config.runtime)
        trigger1.run()
        self.config.runtime.start_spec()
        trigger2 = pyspec.framework.SpecTestTrigger(self.fixture2,
                runtime_option=self.config.runtime)
        trigger2.run()


class Behavior_LegacyCodeTestProxy(object):
    class LegacyPeopleClass(object):
        def __init__(self, name, age):
            self.name = name
            self.age = age

        def get_name(self):
            return self.name

        def set_age(self, age):
            self.age = age

    @context(group=1)
    def method_call_to_the_proxy_of_legacy_code(self):
        legacy_object = self.LegacyPeopleClass("Taro", 32)
        self.config = setting.PySpecConfig()
        proxy = test_proxy(legacy_object, runtime_option=self.config.runtime)
        print proxy.get_name()

    @spec(group=1)
    def should_record_and_verify_the_method_call_and_return_values(self):
        About(len(self.config.runtime.legacy_data.values()[0])).should_equal(1)
        About(self.config.runtime.recording_flag).should_be_true()

    @context(group=2)
    def attribute_access_to_the_proxy_of_legacy_code(self):
        legacy_object = self.LegacyPeopleClass("Taro", 32)
        self.config = setting.PySpecConfig()
        proxy = test_proxy(legacy_object, runtime_option=self.config.runtime)
        print proxy.name

    @spec(group=2)
    def should_not_record_attribute_access(self):
        About(len(self.config.runtime.legacy_data.values()[0])).should_equal(0)
        About(self.config.runtime.recording_flag).should_be_true()

    @context(group=3)
    def proxies_of_legacy_code_that_are_not_changed(self):
        self.legacy_object = self.LegacyPeopleClass("Taro", 32)
        #recording
        self.config = setting.PySpecConfig()
        proxy1 = test_proxy(self.legacy_object,
                runtime_option=self.config.runtime)
        proxy1.get_name()

    @spec(group=3)
    def should_not_raise_exception(self):
        #run second test
        self.config.runtime.start_spec()
        proxy2 = test_proxy(self.legacy_object,
                runtime_option=self.config.runtime)
        proxy2.get_name()

    @context(group=4)
    def proxies_of_legacy_code_these_return_values_are_changed(self):
        legacy_object1 = self.LegacyPeopleClass("Taro", 32)
        self.legacy_object2 = self.LegacyPeopleClass("Jiro", 30)
        #recording
        self.config = setting.PySpecConfig()
        proxy1 = test_proxy(legacy_object1, runtime_option=self.config.runtime)
        proxy1.get_name() # return "Taro"

    @spec(group=4, expected=AssertionError)
    def should_raise_exception(self):
        #run second test
        self.config.runtime.start_spec()
        proxy2 = test_proxy(self.legacy_object2,
                runtime_option=self.config.runtime)
        print proxy2.get_name() # return "Jiro"

    @spec(group=4)
    def should_not_raise_exception_if_return_values_are_ignored(self):
        #run second test
        self.config.runtime.start_spec()
        proxy2 = test_proxy(self.legacy_object2, check_return=False,
                runtime_option=self.config.runtime)
        print proxy2.get_name() # return "Jiro"

    """@spec(group=3)
    def should_not_raise_if_args_are_changed_with_ignore_args_flag(self):
        #run second test
        self.config.runtime.start_spec()
        proxy2 = test_proxy(self.legacy_object2, config=self.config,
                            check_return=False, check_args=False)
        print proxy2.get_name("") # return "Jiro"""


if __name__ == "__main__":
    run_test()
