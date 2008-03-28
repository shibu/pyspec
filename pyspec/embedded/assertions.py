# -*- coding: ascii -*-

"""This module implements assertion functions.
"""

__pyspec = 1
__verifiers = []

import re
import compat_ironpython
from setting import config
language = config.language

def About(actual):
    global __verifiers
    for check_function, verifier in __verifiers:
        if check_function(actual):
            return verifier(actual)
    return StandardVerifier(actual)


class VerifierBase(object):
    _target_splitter = re.compile(r"About\((.*)\).should")

    __slots__ = ("actual",)
    def __init__(self, actual):
        self.actual = actual

    @classmethod
    def _get_target(cls):
        source = compat_ironpython.get_source_code(3)
        if source is None:
            return None
        match = cls._target_splitter.search(source)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _source(source, actual):
        if source is not None:
            return "%s" % source
        return "<%r>" % actual

    @classmethod
    def _value_with_source(cls, source, actual):
        if source is not None:
            value = cls._value(actual)
            if source == value:
                return value
            return "%s(=%s)" % (source, cls._value(actual))
        return "<%r>" % actual

    @staticmethod
    def _value(value):
        if isinstance(value, basestring):
            return '"%s"' % value
        return '%s' % str(value)


class StandardVerifier(VerifierBase):
    """Verification tool class.

    This class have many verification methods to define behavior.

    usage::
        a = 100
        About(a).should_equal(10)
    """
    def should_equal(self, expected):
        """Test the value is equal to a target.

        Fail if the two objects are unequal as determined by the '=='
        operator.

        usage::
            a = 2
            About(a).should_equal(2) # OK!
            About(a).should_equal(3) # Fail!

        @param expected: target value
        """
        config.runtime.ignore_stack = True
        source = self._get_target()
        if not expected == self.actual:
            msg = language.get("should_equal", "fail",
                   variable_name=self._source(source, self.actual),
                   expected_value=self._value(expected),
                   actual_value=self._value(self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_equal", "ok",
               variable_name=self._source(source, self.actual),
               expected_value=self._value(expected))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False
        return msg

    def should_not_equal(self, unexpected, msg = None):
        """Test the value is unequal to a target.

        Fail if the two objects are equal as determined by the '=='
        operator.

        usage::
            a = 2
            About(a).should_not_equal(3) # OK!
            About(a).should_not_equal(2) # Fail!

        @param expected: target value
        """
        config.runtime.ignore_stack = True
        source = self._get_target()
        if unexpected == self.actual:
            msg = language.get("should_not_equal", "fail",
                   variable_name=self._source(source, self.actual),
                   unexpected_value=self._value(unexpected))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_not_equal", "ok",
               variable_name=self._value_with_source(source, self.actual),
               unexpected_value=self._value(unexpected))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        ignroe_stack = False
        return msg

    def should_equal_nearly(self, expected, delta=None):
        """Test the value is near to a target value.

        Fail if the difference of two floating point number is
        more than 'tolerance'.

        usage:
            a = 200.0
            About(a).should_equal_nearly(201.0, 2.0) # OK!
            About(a).should_equal_nearly(203.0, 2.0) # Fail!

        @param expected: target value
        @type  expected: float
        @param delta: allowable margin of error(default=expected*0.01)
        @type  delta: float
        """
        config.runtime.ignore_stack = True
        if delta is None:
            delta = expected * 0.01
        source = self._get_target()
        if abs(expected - self.actual) > delta:
            msg = language.get("should_equal_nearly", "fail",
                   variable_name=self._source(source, self.actual),
                   expected_value=self._value(expected), delta=delta,
                   actual_value=self._value(self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_equal_nearly", "ok",
               variable_name=self._source(source, self.actual),
               expected_value=self._value(expected), delta=delta)
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_not_equal_nearly(self, expected, delta=None):
        """Test the value is far from a target value.

        Fail if the difference of two floating point number is
        less than 'tolerance'.

        usage:
            a = 200.0
            About(a).should_equal_nearly(300.0, 2.0) # OK!
            About(a).should_equal_nearly(201.0, 2.0) # Fail!

        @param expected: target value
        @type  expected: float
        @param tolerance: disallowable margin of error(default=expected*0.01)
        @type  tolerance: float

        """
        config.runtime.ignore_stack = True
        if delta is None:
            delta = expected * 0.01
        source = self._get_target()
        if abs(expected - self.actual) < delta:
            msg = language.get("should_not_equal_nearly", "fail",
                   variable_name=self._source(source, self.actual),
                   expected_value=self._value(expected), delta=delta)
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_not_equal_nearly", "ok",
               variable_name=self._source(source, self.actual),
               expected_value=self._value(expected), delta=delta)
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_be_true(self, msg=""):
        """Fail if value is not True."""
        config.runtime.ignore_stack = True
        source = self._get_target()
        if not self.actual:
            msg = language.get("should_be_true", "fail",
                   variable_name=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_be_true", "ok",
               variable_name=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_be_false(self, msg=""):
        """Fail if value is not False."""
        config.runtime.ignore_stack = True
        source = self._get_target()
        if self.actual:
            msg = language.get("should_be_false", "fail",
                   variable_name=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_be_false", "ok",
               variable_name=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_be_none(self, msg=""):
        """Fail if value is not None."""
        config.runtime.ignore_stack = True
        source = self._get_target()
        if self.actual is not None:
            msg = language.get("should_be_none", "fail",
                   variable_name=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_be_none", "ok",
               variable_name=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_not_be_none(self, msg=""):
        """Fail if value is None."""
        config.runtime.ignore_stack = True
        source = self._get_target()
        if self.actual is None:
            msg = language.get("should_not_be_none", "fail",
                   variable_name=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_not_be_none", "ok",
               variable_name=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_be_same_variable_splitter = re.compile(
                                    r"About\((.*)\).should_be_same\((.*)\)")

    def should_be_same(self, expected, msg = None):
        """Fail if the two objects are different as determined by the 'is'
             operator.
        """
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
            match1 = None
            match2 = None
        else:
            m = self._should_be_same_variable_splitter.search(source)
            match1 = m.group(1)
            match2 = m.group(2)
        if not expected is self.actual:
            try:
                msg = language.get("should_be_same", "fail",
                        actual_expression=self._value_with_source(match1, self.actual),
                        expected_expression=self._value_with_source(match2, expected))
            except:
                msg = language.get("should_be_same", "fail",
                        actual_expression=self.actual,
                        expected_expression=expected)
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        try:
            msg = language.get("should_be_same", "ok",
                    actual_expression=self._value_with_source(match1, self.actual),
                    expected_expression=self._value_with_source(match2, expected))
        except:
            msg = language.get("should_be_same", "ok",
                    actual_expression=self.actual,
                    expected_expression=expected)
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_not_be_variable_splitter = re.compile(
                                r"About\((.*)\).should_not_be_same\((.*)\)")

    def should_not_be_same(self, expected, msg = None):
        """Fail if the two objects are different as determined by the 'is'
             operator.
        """
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
             match1 = None
             match2 = None
        else:
             m = self._should_not_be_variable_splitter.search(source)
             match1 = m.group(1)
             match2 = m.group(2)
        if expected is self.actual:
            try:
                msg = language.get("should_not_be_same", "fail",
                        actual_expression=self._value_with_source(match1, self.actual),
                        expected_expression=self._value_with_source(match2, expected))
            except:
                msg = language.get("should_not_be_same", "fail",
                        actual_expression=self.actual,
                        expected_expression=expected)
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        try:
            msg = language.get("should_not_be_same", "ok",
                    actual_expression=self._value_with_source(match1, self.actual),
                    expected_expression=self._value_with_source(match2, expected))
        except:
            msg = language.get("should_not_be_same", "ok",
                    actual_expression=self.actual,
                    expected_expression=expected)
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_include_variable_splitter = re.compile(
                                    r"About\((.*)\).should_include\((.*)\)")

    def should_include(self, expected, msg = None):
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
             match1 = None
             match2 = None
        else:
             m = self._should_include_variable_splitter.search(source)
             match1 = m.group(1)
             match2 = m.group(2)
        if (not hasattr(self.actual, "__contains__")
            and not hasattr(self.actual, "__iter__")):
            msg = language.get("should_include", "error",
                    variable_name=self._value_with_source(match1, self.actual))
            config.runtime.ignore_stack = False
            raise TypeError(msg)
        elif not expected in self.actual:
            msg = language.get("should_include", "fail",
                    sequence=self._value_with_source(match1, self.actual),
                    expected_value=self._value_with_source(match2, expected))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_include", "ok",
                sequence=self._value_with_source(match1, self.actual),
                expected_value=self._value_with_source(match2, expected))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_not_include_variable_splitter = re.compile(
                                    r"About\((.*)\).should_not_include\((.*)\)")

    def should_not_include(self, expected, msg = None):
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
             match1 = None
             match2 = None
        else:
             m = self._should_not_include_variable_splitter.search(source)
             match1 = m.group(1)
             match2 = m.group(2)
        if (not hasattr(self.actual, "__contains__")
            and not hasattr(self.actual, "__iter__")):
            msg = language.get("should_not_include", "error",
                    variable_name=self._value_with_source(match1, self.actual))
            config.runtime.ignore_stack = False
            raise TypeError, msg
        elif expected in self.actual:
            try:
                msg = language.get("should_not_include", "fail",
                       sequence=self._value_with_source(match1, self.actual),
                       expected_value=self._value_with_source(match2, expected))
            except:
                msg = language.get("should_not_include", "fail",
                        sequence=self.actual, expected_value=expected)
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        try:
            msg = language.get("should_not_include", "ok",
                    sequence=self._value_with_source(match1, self.actual),
                    expected_value=self._value_with_source(match2, expected))
        except:
            msg = language.get("should_not_include", "ok",
                    sequence=self.actual, expected_value=expected)
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_be_empty(self, msg = None):
        config.runtime.ignore_stack = True
        source = self._get_target()
        if not hasattr(self.actual, "__len__"):
            msg = language.get("should_be_empty", "error",
                    sequence=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        if len(self.actual) != 0:
            msg = language.get("should_be_empty", "fail",
                    sequence=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_be_empty", "ok",
                sequence=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_not_be_empty(self, msg = None):
        config.runtime.ignore_stack = True
        source = self._get_target()
        if not hasattr(self.actual, "__len__"):
            msg = language.get("should_not_be_empty", "error",
                    sequence=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        if len(self.actual) == 0:
            msg = language.get("should_not_be_empty", "fail",
                    sequence=self._source(source, self.actual))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_not_be_empty", "ok",
                sequence=self._source(source, self.actual))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_be_in_variable_splitter = re.compile(
                                    r"About\((.*)\).should_be_in\((.*)\)")

    def should_be_in(self, expected, msg=None):
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
             match1 = None
             match2 = None
        else:
             m = self._should_be_in_variable_splitter.search(source)
             match1 = m.group(1)
             match2 = m.group(2)
        try:
            result = self.actual not in expected
        except TypeError:
            msg = language.get("should_be_in", "error",
                     sequence=self._value_with_source(match2, expected))
            raise TypeError(msg)
        if result:
            msg = language.get("should_be_in", "fail",
                     actual_value=self._value_with_source(match1, self.actual),
                     sequence=self._value_with_source(match2, expected))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_be_in", "ok",
                 actual_value=self._value_with_source(match1, self.actual),
                 sequence=self._value_with_source(match2, expected))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    _should_not_be_in_variable_splitter = re.compile(
                                    r"About\((.*)\).should_not_be_in\((.*)\)")

    def should_not_be_in(self, expected, msg=None):
        config.runtime.ignore_stack = True
        source = compat_ironpython.get_source_code()
        if source is None:
             match1 = None
             match2 = None
        else:
             m = self._should_not_be_in_variable_splitter.search(source)
             match1 = m.group(1)
             match2 = m.group(2)
        try:
            result = self.actual in expected
        except TypeError:
            msg = language.get("should_not_be_in", "error",
                     sequence=self._value_with_source(match2, expected))
            raise TypeError(msg)
        if result:
            msg = language.get("should_not_be_in", "fail",
                     actual_value=self._value_with_source(match1, self.actual),
                     sequence=self._value_with_source(match2, expected))
            config.runtime.ignore_stack = False
            raise AssertionError(msg)
        msg = language.get("should_not_be_in", "ok",
                 actual_value=self._value_with_source(match1, self.actual),
                 sequence=self._value_with_source(match2, expected))
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False

    def should_not_be_changed(self, reset=False):
        config.runtime.ignore_stack = True
        variable = self._get_target()
        value, changed = config.runtime.get_recorded_value(variable,
                self.actual, reset)
        if not changed:
            if value != self.actual:
                config.runtime.ignore_stack = False
                msg = language.get("should_not_be_changed", "fail",
                        target=self._value_with_source(variable, value),
                        actual_value = self.actual)
                raise AssertionError(msg)
            else:
                msg = language.get("should_not_be_changed", "ok",
                        target=self._value_with_source(variable, value))
        else:
            msg = language.get("should_not_be_changed", "recorded",
                   target=self._value_with_source(variable, value))
            config.runtime.recording_flag = True
        if config.runtime.report_out:
            config.runtime.report_out.write(msg)
        config.runtime.ignore_stack = False


def regist_test_verifier(check_function, verifier):
    global __verifiers
    __verifiers.append((check_function, verifier))
