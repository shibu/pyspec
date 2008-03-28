# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework
import pyspec.reloader as reloader
import StringIO, string


class AssertionMethods_Behaivior(object):
    @spec
    def pyspec_should_describe_exception(self):
        raise ValueError("abc")

    @spec
    def pyspec_should_find_the_value_is_not_True(self):
        a = False
        About(a).should_be_true()

    @spec
    def pyspec_should_describe_the_value_is_True(self):
        a = True
        About(a).should_be_true()

    @spec
    def pyspec_should_find_the_value_is_not_False(self):
        a = True
        About(a).should_be_false()

    @spec
    def pyspec_should_describe_the_value_is_False(self):
        a = False
        About(a).should_be_false()

    @spec
    def pyspec_should_find_the_value_is_not_None(self):
        a = True
        About(a).should_be_none()

    @spec
    def pyspec_should_describe_the_value_is_None(self):
        a = None
        About(a).should_be_none()

    @spec
    def pyspec_should_find_the_value_is_None(self):
        a = None
        About(a).should_not_be_none()

    @spec
    def pyspec_should_describe_the_value_is_not_None(self):
        a = True
        About(a).should_not_be_none()

    @spec
    def pyspec_should_find_the_values_does_not_equal(self):
        a = "abc"
        About(a).should_equal("def")

    @spec
    def pyspec_should_describe_the_values_equal(self):
        a = "abc"
        About(a).should_equal("abc")

    @spec
    def pyspec_should_find_the_values_are_not_near(self):
        a = 1.1
        About(a).should_equal_nearly(1.3, 0.1)

    @spec
    def pyspec_should_describe_the_values_are_near(self):
        a = 1.1
        About(a).should_equal_nearly(1.2, 0.2)

    @spec
    def pyspec_should_find_the_values_equal(self):
        a = "abc"
        About(a).should_not_equal("abc")

    @spec
    def pyspec_should_describe_the_values_do_not_equal(self):
        a = "abc"
        About(a).should_not_equal("def")

    @spec
    def pyspec_should_find_the_objects_are_not_same(self):
        a = xrange(5)
        b = xrange(5) # diffenent object!
        About(a).should_be_same(b)

    @spec
    def pyspec_should_describe_the_objects_are_same(self):
        a = xrange(5)
        b = a # same object!
        About(a).should_be_same(b)

    @spec
    def pyspec_should_find_the_objects_are_same(self):
        a = xrange(5)
        b = a # same object!
        About(a).should_not_be_same(b)

    @spec
    def pyspec_should_describe_the_objects_are_not_same(self):
        a = xrange(5)
        b = xrange(5) # diffenent object!
        About(a).should_not_be_same(b)

    class IgnoreTestCase(object):
        @ignore
        @spec
        def ignore_test(self):
            pass

    @spec
    def pyspec_can_ignore_the_method_which_have_ignore_decoretor(self):
        sample = pyspec.framework.SpecTestTrigger(self.IgnoreTestCase())
        result = sample.run()
        About(result.ignore_count).should_equal(1)

    @spec
    def pyspec_has_method_that_describe_the_flow_is_bad(self):
        Verify.fail("fail test")

    @spec(expected=pyspec.IgnoreTestCase)
    def pyspec_has_method_that_describe_the_spec_should_be_ignored(self):
        Verify.ignore("ignore test")

    @spec
    def should_include__success(self):
        a = range(5)
        About(a).should_include(3)

    @spec
    def should_include__fail(self):
        a = range(5)
        About(a).should_include(10)

    @spec(expected=TypeError)
    def should_include__error(self):
        a = 1
        About(a).should_include(1)

    @spec
    def should_not_include__success(self):
        a = range(5)
        About(a).should_not_include(10)

    @spec
    def should_not_include__fail(self):
        a = range(5)
        About(a).should_not_include(3)

    @spec(expected=TypeError)
    def should_not_include__error(self):
        a = 1
        About(a).should_not_include(1)

    @spec
    def should_be_in__success(self):
        About(2).should_be_in(range(5))

    @spec
    def should_be_in__fail(self):
        About(10).should_be_in(range(5))

    @spec
    def should_be_in__error(self):
        About(10).should_be_in(1)

    @spec
    def should_not_be_in__success(self):
        About(10).should_not_be_in(range(5))

    @spec
    def should_not_be_in__fail(self):
        About(2).should_not_be_in(range(5))

    @spec
    def should_not_be_in__error(self):
        About(10).should_not_be_in(1)

    @spec
    def should_not_be_changed__success(self):
        value = 10
        About(value).should_not_be_changed()

    @spec
    def should_not_be_changed__fail(self):
        import random
        value = random.randint(0, 1000)
        About(value).should_not_be_changed()

class FailDataProvider(object):
        @classmethod
        @data_provider(key=("i", "j"))
        def generate_pair_data(cls):
            #key length and result data length is not same.
            return [(1, 2, 3, 4), (3, 4, 5, 6)]

        @spec
        def data_provider_error(self, i, j):
            pass


if __name__ == "__main__":
    run_test()
