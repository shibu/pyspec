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
    @spec(expected=ValueError)
    def pyspec_should_describe_exception(self):
        raise ValueError("abc")

    @spec(expected=AssertionError)
    def pyspec_should_find_the_value_is_not_True(self):
        a = False
        About(a).should_be_true()

    @spec
    def pyspec_should_describe_the_value_is_True(self):
        a = True
        About(a).should_be_true()

    @spec(expected=AssertionError)
    def pyspec_should_find_the_value_is_not_False(self):
        a = True
        About(a).should_be_false()

    @spec
    def pyspec_should_describe_the_value_is_False(self):
        a = False
        About(a).should_be_false()

    @spec(expected=AssertionError)
    def pyspec_should_find_the_value_is_not_None(self):
        a = True
        About(a).should_be_none()

    @spec
    def pyspec_should_describe_the_value_is_None(self):
        a = None
        About(a).should_be_none()

    @spec(expected=AssertionError)
    def pyspec_should_find_the_value_is_None(self):
        a = None
        About(a).should_not_be_none()

    @spec
    def pyspec_should_describe_the_value_is_not_None(self):
        a = True
        About(a).should_not_be_none()

    @spec(expected=AssertionError)
    def pyspec_should_find_the_values_does_not_equal(self):
        a = "abc"
        About(a).should_equal("def")

    @spec
    def pyspec_should_describe_the_values_equal(self):
        a = "abc"
        About(a).should_equal("abc")

    @spec(expected=AssertionError)
    def pyspec_should_find_the_values_are_not_near(self):
        a = 1.1
        About(a).should_equal_nearly(1.3, 0.1)

    @spec
    def pyspec_should_describe_the_values_are_near(self):
        a = 1.1
        About(a).should_equal_nearly(1.2, 0.2)

    @spec(expected=AssertionError)
    def pyspec_should_find_the_values_equal(self):
        a = "abc"
        About(a).should_not_equal("abc")

    @spec
    def pyspec_should_describe_the_values_do_not_equal(self):
        a = "abc"
        About(a).should_not_equal("def")

    @spec(expected=AssertionError)
    def pyspec_should_find_the_objects_are_not_same(self):
        a = xrange(5)
        b = xrange(5) # diffenent object!
        About(a).should_be_same(b)

    @spec
    def pyspec_should_describe_the_objects_are_same(self):
        a = xrange(5)
        b = a # same object!
        About(a).should_be_same(b)

    @spec(expected=AssertionError)
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

    @spec(expected=AssertionError)
    def pyspec_has_method_that_describe_the_flow_is_bad(self):
        Verify.fail("fail test")

    @spec(expected=pyspec.IgnoreTestCase)
    def pyspec_has_method_that_describe_the_spec_should_be_ignored(self):
        Verify.ignore("ignore test")

    @spec
    def should_include__success(self):
        a = range(5)
        About(a).should_include(3)

    @spec(expected=AssertionError)
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

    @spec(expected=AssertionError)
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

    @spec(expected=AssertionError)
    def should_be_in__fail(self):
        About(10).should_be_in(range(5))

    @spec(expected=TypeError)
    def should_be_in__error(self):
        About(10).should_be_in(1)

    @spec
    def should_not_be_in__success(self):
        About(10).should_not_be_in(range(5))

    @spec(expected=AssertionError)
    def should_not_be_in__fail(self):
        About(2).should_not_be_in(range(5))

    @spec(expected=TypeError)
    def should_not_be_in__error(self):
        About(10).should_not_be_in(1)


class context_and_filalize_Behavior(object):
    class context_and_filalize_Fixture(object):
        def __init__(self, mock):
            self.mock = mock

        def __call__(self):
            import copy
            return copy.copy(self)

        @context
        def context(self):
            self.mock.context()

        @spec_finalize
        def spec_finalize(self):
            self.mock.spec_finalize()

        @spec
        def spec(self):
            self.mock.spec()

    @context(group=1)
    def context__and__spec_finalize(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.context()
        recorder.spec()
        recorder.spec_finalize()
        self.mock = recorder._get_mock_object_()
        fixture = self.context_and_filalize_Fixture(self.mock)
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=1)
    def should_be_called1(self):
        self.trigger.run()
        self.mock._verify_()

    class class_context_and_class_filalize_Fixture(object):
        def __init__(self, mock):
            self.mock = mock

        def __call__(self):
            import copy
            return copy.copy(self)

        @context
        def context(self):
            self.mock.context()

        @class_context
        def class_context(self):
            self.mock.class_context()

        @class_finalize
        def class_finalize(self):
            self.mock.class_finalize()

        @spec
        def spec1(self):
            self.mock.spec1()

        @spec
        def spec2(self):
            self.mock.spec2()

    @context(group=2)
    def class_context__and__class_finalize(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.class_context()
        recorder.context()
        recorder.spec1()
        recorder.context()
        recorder.spec2()
        recorder.class_finalize()
        self.mock = recorder._get_mock_object_()
        fixture = self.class_context_and_class_filalize_Fixture(self.mock)
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=2)
    def should_be_called2(self):
        self.trigger.run()
        self.mock._verify_()

    class FailableFixture:
        def __init__(self, mock, fail_point):
            self.mock = mock
            self.fail_point = fail_point

        def __call__(self):
            import copy
            return copy.copy(self)

        @context
        def context(self):
            if self.fail_point == "context":
                raise ValueError("fail")
            self.mock.context()

        @spec_finalize
        def spec_finalize(self):
            self.mock.spec_finalize()

        @class_context
        def class_context(self):
            self.mock.class_context()

        @class_finalize
        def class_finalize(self):
            self.mock.class_finalize()

        @spec
        def spec(self):
            if self.fail_point == "spec":
                raise ValueError("fail")
            self.mock.spec()

    @context(group=3)
    def Fixture_that_raises_exception_at_spec_method(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.class_context()
        recorder.context()
        recorder.spec_finalize()
        recorder.class_finalize()
        self.mock = recorder._get_mock_object_()
        fixture = self.FailableFixture(self.mock, fail_point="spec")
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)

    @spec(group=3)
    def spec_finalize__should_be_run(self):
        try:
            self.trigger.run()
        except:
            pass
        self.mock._verify_()

    @context(group=4)
    def Fixture_that_raises_exception_at_context_method(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.class_context()
        recorder.class_finalize()
        self.mock = recorder._get_mock_object_()
        fixture = self.FailableFixture(self.mock, fail_point="context")
        self.trigger = pyspec.framework.SpecTestTrigger(fixture)


    @spec(group=4)
    def class_finalize__should_be_run_when_context_failed(self):
        try:
            self.trigger.run()
        except:
            pass
        self.mock._verify_()


class TestMethodCategorizer(object):
    def method_with_category(self):
        """sample method.
        @category sample
        """
        pass

    def method_without_category(self):
        """sample method."""
        pass

    def method_no_docstring(self):
        pass

    @context
    def create_categorizer(self):
        self.categorizer = reloader.MethodCategorizer()
        self.categorizer.regist_method(self.method_with_category)
        self.categorizer.regist_method(self.method_without_category)

    @spec
    def have_category(self):
        docstring1 = "@category init"
        docstring2 = "@category init test"
        docstring3 = "no category"
        About(self.categorizer.search_docstring(docstring1)).should_equal("init")
        About(self.categorizer.search_docstring(docstring2)).should_equal("init")
        About(self.categorizer.search_docstring(docstring3)).should_equal(None)

    @spec
    def check_method(self):
        About(self.categorizer.check_method(self.method_with_category)).should_equal("sample")
        About(self.categorizer.check_method(self.method_without_category)).should_equal(None)
        About(self.categorizer.check_method(self.method_no_docstring)).should_equal(None)

    @spec
    def find(self):
        print self.categorizer.methods
        About(self.categorizer.find_category(id(self.method_with_category.im_func.func_code))).should_equal("sample")
        About(self.categorizer.find_category(id(self.method_without_category.im_func.func_code))).should_equal(None)


class DebugSupport_Behavior(object):
    @context(group=1)
    def dprint_function_result(self):
        test_value = 10
        self.variable_name = "test_value"
        self.value = test_value
        filename = os.path.split(__file__)[1].replace(".pyc", ".py")
        filename = filename.replace(".pyo", ".py")
        self.fineinfo = string.Template("@$filename").substitute(
                            filename=filename)
        stringio = StringIO.StringIO()
        dprint(test_value, file=stringio)
        self.result = stringio.getvalue()

    @spec(group=1)
    def should_contain_value_and_variable(self):
        About(self.result).should_include(self.variable_name)
        About(self.result).should_include(str(self.value))

    @spec(group=1)
    def should_contain_file_info(self):
        About(self.result).should_include(self.fineinfo)

    @context(group=2)
    def dprint_function_result_with_2_variables(self):
        var1 = 10
        var2 = 20
        self.variable_name1 = "var1"
        self.variable_name2 = "var2"
        self.value1 = var1
        self.value2 = var2
        stringio = StringIO.StringIO()
        dprint(var1, var2, file=stringio)
        self.result = stringio.getvalue()

    @spec(group=2)
    def should_contain_all_values_and_variables(self):
        About(self.result).should_include(self.variable_name1)
        About(self.result).should_include(str(self.value1))
        About(self.result).should_include(self.variable_name2)
        About(self.result).should_include(str(self.value2))

    @context(group=3)
    def dprint_function_result_with_original_separator(self):
        var1 = 10
        var2 = 20
        stringio = StringIO.StringIO()
        dprint(var1, var2, file=stringio, sep=" : ")
        self.result = stringio.getvalue()

    @spec(group=3)
    def should_change_separator(self):
        About(self.result).should_include("var1=10 : var2=20")

    @context(group=4)
    def dprint_function_result_with_original_end_charactor(self):
        test_value = 10
        stringio = StringIO.StringIO()
        dprint(test_value, file=stringio, end="</br>")
        self.result = stringio.getvalue()

    @spec(group=4)
    def should_change_end_charactor(self):
        About(self.result).should_include("test_value=10</br>")

    @context(group=5)
    def dprint_function_result_with_original_variable_separator(self):
        test_value = 10
        stringio = StringIO.StringIO()
        dprint(test_value, file=stringio, varsep=" => ")
        self.result = stringio.getvalue()

    @spec(group=5)
    def should_change_variable_separator(self):
        About(self.result).should_include("test_value => 10")

    @context(group=6)
    def dprint_function_result_without_fileinfo(self):
        test_value = 10
        filename = os.path.split(__file__)[1]
        filename = os.path.splitext(filename)[0]
        self.fineinfo = string.Template("@${filename}.py").substitute(
                            filename=filename)
        stringio = StringIO.StringIO()
        dprint(test_value, file=stringio, fileinfo=False)
        self.result = stringio.getvalue()

    @spec(group=6)
    def should_skip_fileinfo(self):
        About(self.result).should_not_include(self.fineinfo)


if __name__ == "__main__":
    run_test()
