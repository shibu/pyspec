# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

import os, sys
from pyspec import *
from pyspec.mockobject import *
import pyspec.util as util

class Struct_Behavior(object):
    @context
    def A_struct_object(self):
        self.struct = util.Struct(key1="abc", key2=123)

    @spec
    def should_store_the_value(self):
        About(self.struct.key1).should_equal("abc")
        About(self.struct.key2).should_equal(123)

    @spec
    def should_rewrite_the_value(self):
        fixture = util.Struct()
        self.struct.key1 = "new_value"
        About(self.struct.key1).should_equal("new_value")

    @spec
    def should_regist_new_key(self):
        self.struct.new_key = "abc"
        About(self.struct.new_key).should_equal("abc")

    @spec(expected=AttributeError)
    def read_error(self):
        a = self.struct.key_not_defined


@spec
def format_xml__can_generate_single_element_XML():
    test_file = MockFile("<ELEM>TEXT</ELEM>")
    util.format_xml(["ELEM", "TEXT"], test_file, "")


@spec
def format_xml__can_generate_nested_elements_XML():
    test_file = MockFile("<ELEM>\n  <CHILD/>\n</ELEM>")
    util.format_xml(["ELEM", ["CHILD"]], test_file)


class TestRelativePath(object):
    @spec
    def relative_path__1(object):
        from_path = "/boot/home/config/bin/pyspec"
        to_path = "/boot/home/config/bin/wxform/form.xrc"
        result = os.path.join(".", "wxform", "form.xrc")
        About(util.relative_path(from_path, to_path)).should_equal(result)

    @spec
    def relative_path__2(object):
        from_path = "/boot/home/config/bin/pyspec"
        to_path = "/boot/home/config/data/wxform/form.xrc"
        result = os.path.join("..", "data", "wxform", "form.xrc")
        About(util.relative_path(from_path, to_path)).should_equal(result)

    if sys.platform == "win32":
        @spec
        def absolute_path__1(object):
            from_path = r"c:\share\bin\pyspec"
            relative_path = r".\wxform\form.xrc"
            result = r"c:\share\bin\wxform\form.xrc"
            About(util.absolute_path(from_path, relative_path)).should_equal(result)
    else:
        @spec
        def absolute_path__2(object):
            from_path = "/share/bin/pyspec"
            relative_path = "./wxform/form.xrc"
            result = os.path.join("/", "share", "bin", "wxform", "form.xrc")
            About(util.absolute_path(from_path, relative_path)).should_equal(result)

        @spec
        def absolute_path__3(object):
            from_path = "/share/bin/pyspec"
            relative_path = "../wxform/form.xrc"
            result = os.path.join("/", "share", "wxform", "form.xrc")
            About(util.absolute_path(from_path, relative_path)).should_equal(result)


class MultiDeligator_Behavior(object):
    class SampleA(object):
        def __init__(self, mock):
            self.mock = mock

        def a(self):
            self.mock.A_a()

        def b(self, i):
            self.mock.A_b(i)

        def return_value(self):
            return "value by A"

    class SampleB(object):
        def __init__(self, mock):
            self.mock = mock

        def a(self):
            self.mock.B_a()

        def b(self, i):
            self.mock.B_b(i)
            return 20

        def return_value(self):
            return "value by B"

    @context
    def A_deligator_with_2_class(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.A_a()
        recorder.B_a()
        recorder.A_b(10)
        recorder.B_b(10)
        self.mock = recorder._get_mock_object_()
        self.deligator = util.MultiDeligator(
                             self.SampleA(self.mock),
                             self.SampleB(self.mock))

    @spec
    def should_broadcast_method_call_with_parameter(self):
        self.deligator.a()
        self.deligator.b(10)
        self.mock._verify_()

    @spec
    def should_return_last_method_value(self):
        About(self.deligator.return_value()).should_equal("value by B")


class create_spec_name__Behavior(object):
    @context(group=1)
    def spec_name_with_single_underline(self):
        self.spec_name = util.create_spec_name("test_method")

    @spec(group=1)
    def should_be_changed_underline_into_space(self):
        About(self.spec_name).should_equal("test method")

    @context(group=2)
    def spec_name_with_double_underlines(self):
        self.spec_name = util.create_spec_name("test_method__should_success")

    @spec(group=2)
    def should_keep_method_name(self):
        About(self.spec_name).should_equal("test_method should success")

    @context(group=3)
    def spec_name_with_multi_underlines(self):
        self.spec_name = util.create_spec_name("test__spec_method__should_fail")

    @spec(group=3)
    def should_keep_even_position_groups_as_a_method_name(self):
        About(self.spec_name).should_equal("test spec_method should fail")


if __name__ == "__main__":
    run_test()
