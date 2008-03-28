# -*- coding: ascii -*-

"""PySpec - Behavior Driven Development Framework -.

This package have many items for BDD. For example, spec definition decorators
and spec verification tools, mock objects, CUI and GUI test runners and so on.

Simple usage (compare it with unittest module sample!)::

    from pyspec import *

    class IntegerArithmentic_Behavior():
        @spec
        def integer_should_support_add(self):  ## test method have @spec decor
            About(1 + 2).should_equal(3)
            About(0 + 1).should_equal(1)
        @spec
        def integer_should_support_mul(self):
            About(0 * 10).should_equal(0)
            About(5 * 8).should_equal(40)

    if __name__ == '__main__':
        run_test()


This software is inspired by unittest module.
I thank Mr.Steve Purcell for his work.

And I must say 'thank you' to Mr. Masaru Ishii too.
He popularized unit test in Japan.

PySpec License
==============

License:  The MIT License
Copyright (c) 2007 Shibukawa Yoshiki

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Related Package
===============

pyspec contains tempita module to generate report.
Its license is the MIT License.

"""

__docformat__ = 'restructuredtext en'

#: The version of pyspec
__version__ = '0.54-pre'
#: The primary author of pyspec
__author__ = 'Shibukawa Yoshiki <yoshiki at shibu.jp>'
#: The URL for pyspec's project page
__url__ = 'http://www.codeplex.com/pyspec'
#: The license governing the use and distribution of pyspec"""
__license__ = 'MIT License'


__pyspec = 1
__test_index = 0


__all__ = (
    "spec",
    "context",
    "class_context",
    "spec_finalize",
    "class_finalize",
    "ignore",
    "data_provider",
    "IgnoreTestCase",
    "Verify",
    "run_test",
    "regist_test_verifier",
    "About",
    "VerifierBase",
    "regist_test_verifier",
    "dprint",
    "config")


from embedded import About, VerifierBase, regist_test_verifier, dprint, config


def get_test_index():
    global __test_index
    __test_index += 1
    return __test_index


class IgnoreTestCase(Exception):
    """Ignore notifier."""


class Verify(object):
    """Verify has support methods for describing spec.
    """
    @staticmethod
    def fail(msg="Stop by user"):
        """Fail always."""
        raise AssertionError(msg)

    @staticmethod
    def ignore(msg="This spec was ignored"):
        """Ignore always."""
        raise IgnoreTestCase(msg)


def spec(method=None, group=None, expected=None, dbc=True):
    """Set BDD method flag."""
    if method is not None:
        append_pyspec_attribute(method, SpecMethodAttribute)
        return method
    return BDDDecorator(group, SpecMethodAttribute, expected, dbc)


def context(method = None, group=None):
    """Set BDD context method flag.

    If you add group, you can make group of context and spec.

    usage:
        @context
        def context_method():

        @context(group=1)
        def context_method_that_have_group()
    """
    if method is not None:
        append_pyspec_attribute(method, ContextMethodAttribute)
        return method
    return BDDDecorator(group, ContextMethodAttribute)


def class_context(method):
    """Set class context method flag."""
    attr = append_pyspec_attribute(method, ContextMethodAttribute)
    attr.is_class = True
    return method


def spec_finalize(method):
    """Set finalize method flag."""
    append_pyspec_attribute(method, FinalizeMethodAttribute)
    return method


def class_finalize(method):
    """Set class finalize method flag."""
    attr = append_pyspec_attribute(method, FinalizeMethodAttribute)
    attr.is_class = True
    return method


def ignore(method):
    """Set spec method ignored flag."""
    attr = append_pyspec_attribute(method, SpecMethodAttribute)
    attr.ignored = True
    return method


def data_provider(key, group=None):
    """Set this method 'data provider' flag."""
    return DataProviderDecorator(key, group)

# -------------
# Spec Register

def append_pyspec_attribute(method, AttributeClass):
    if not hasattr(method, "__pyspec_attribute"):
        method.__pyspec_attribute = AttributeClass()
    return getattr(method, "__pyspec_attribute")


class PySpecAttribute(object):
    __slots__ = ("is_context", "is_finalize", "is_data_provider", "index")
    def __init__(self):
        """set test decorator.
        @category load.registmethod
        """
        self.is_context = False
        self.is_finalize = False
        self.is_data_provider = False
        self.index = get_test_index()


class SpecMethodAttribute(PySpecAttribute):
    __slots__ = PySpecAttribute.__slots__ + ("timeout", "ignored", "groups",
                                             "expected", "dbc")
    def __init__(self):
        super(SpecMethodAttribute, self).__init__()
        self.timeout = 100.0
        self.ignored = False
        self.groups = None
        self.expected = None
        self.dbc = True

    def set_group(self, group):
        """group attribute is used by BDD.
        Spec method uses same group contexts.
        """
        if type(group) in (list, tuple):
            self.groups = group
        else:
            self.groups = (group,)

    def set_expected(self, expected):
        self.expected = expected

    def set_dbc(self, dbc):
        self.dbc = dbc


class ContextMethodAttribute(PySpecAttribute):
    __slots__ = PySpecAttribute.__slots__ + ("is_class", "group")
    def __init__(self):
        super(ContextMethodAttribute, self).__init__()
        self.is_context = True
        self.is_class = False
        self.group = None

    def context(self, test_fixture, context_method):
        method = getattr(test_fixture, context_method.name())
        method()

    def set_group(self, group):
        if type(group) in (list, tuple):
            raise TypeError("context's group argument cannot accept list, tuple.")
        else:
            self.group = group


class FinalizeMethodAttribute(PySpecAttribute):
    __slots__ = PySpecAttribute.__slots__ + ("is_class",)
    def __init__(self):
        super(FinalizeMethodAttribute, self).__init__()
        self.is_finalize = True
        self.is_class = False

    def finalize(self, test_fixture, finalize_method):
        method = getattr(test_fixture, finalize_method.name())
        method()


class DataProviderAttribute(PySpecAttribute):
    __slots__ = PySpecAttribute.__slots__ + ("key", "group")
    def __init__(self):
        super(DataProviderAttribute, self).__init__()
        self.is_data_provider = True
        self.key = None
        self.group = None


class BDDDecorator(object):
    """BDD method decorator.
    This object contains grouping types.
    """
    def __init__(self, group, Attribute, expected=None, dbc=None):
        self.group = group
        self.expected = expected
        self.dbc = dbc
        self.Attribute = Attribute

    def __call__(self, method):
        """Decorate spec options."""
        attr = append_pyspec_attribute(method, self.Attribute)
        attr.set_group(self.group)
        if self.dbc is not None:
            attr.set_dbc(self.dbc)
        if self.expected is not None:
            attr.set_expected(self.expected)
        return method


class DataProviderDecorator(object):
    """Data provider method decorator."""
    def __init__(self, key, group):
        self.key = key
        self.group = group

    def __call__(self, method):
        attr = append_pyspec_attribute(method, DataProviderAttribute)
        attr.key = self.key
        attr.group = self.group
        return method


def run_test():
    """Easy test launcher method.

    usage:
        from pyspec import *

        @spec
        def easy_test():
            About(2 + 1).should_equal(2) # wrong

        if __name__ == "__main__":
            run_test()
    """
    import pyspec.cui
    pyspec.cui.CUISpecTestRunner(auto=True).run()
