# -*- coding: ascii -*-

"""PySpec mock objects
"""

__pyspec = 1
import pyspec
import copy
from util import create_method_repr
from pyspec.embedded import config


class MockResult(object):
    def __init__(self, parent_method):
        self.parent = parent_method

    def result(self, result_value):
        self.parent.result_value = result_value
        if self.parent.is_print:
            print "    <= %s" % result_value

    def __eq__(self, result_value):
        self.result(result_value)
        return True

    def repeat(self, count):
        self.parent.repeat(count)
        return self

    def with_any_parameter(self):
        self.parent.with_any_parameter = True
        return self


class MockMethod(object):
    __slots__ = ("name", "is_recording", "is_print", "result_value",
                 "args", "kwargs", "parent", "with_any_parameter")
    def __init__(self, parent, name, is_print=False):
        self.name = name
        self.is_recording = True
        self.is_print = is_print
        self.result_value = None
        self.args = []
        self.kwargs = {}
        self.parent = parent
        self.with_any_parameter = False

    def call(self, name):
        if name != self.name:
            raise AssertionError("Mock: expected function name is %s(), but was %s()" % (self.name, name))
        return self

    def repeat(self, count):
        for i in xrange(count-1):
            self.parent._methods.append(self)

    def __call__(self, *args, **kwargs):
        if self.is_recording:
            if self.is_print:
                print "Recording: %s" % self.str_for_status(args, kwargs)
            self.args = args
            self.kwargs = kwargs
            return MockResult(self)
        else:
            if self.is_print:
                if self.result_value is not None:
                    result = " => %s" % self.result_value
                else:
                    result = ""
                print "Calling: %s%s" \
                        % (self.str_for_status(args, kwargs), result)
            if not self.with_any_parameter:
                if args != self.args:
                    raise AssertionError(
                          "Mock: expected args are %r, but was %r" \
                              % (self.args, args))
                if kwargs != self.kwargs:
                    raise AssertionError(
                          "Mock: expected kwargs are %r, but was %r" \
                              % (self.kwargs, kwargs))
            return self.result_value

    def str_for_status(self, args, kwargs):
        return "MockObject.%s" % create_method_repr(self.name, args, kwargs)

    def __str__(self):
        args = ", ".join((repr(arg) for arg in self.args))
        kwargs = ", ".join(("%s=%s" % (key, repr(value)) \
                 for key, value in self.kwargs.iteritems()))
        if args != "" and kwargs != "":
            argstring = "%s, %s" % (args, kwargs)
        elif args != "":
            argstring = args
        else:
            argstring = kwargs

        return "    %s(%s) = %r" % (self.name, argstring, self.result_value)

    def copy(self):
        new_method = copy.copy(self)
        new_method.is_recording = False
        new_method.parent = None
        return new_method


class MockObjectRecorder(object):
    def __init__(self, is_print = False):
        self._is_print = is_print
        self._methods = []

    def __getattribute__(self, name):
        try:
            attr = super(MockObjectRecorder, self).__getattribute__(name)
            return attr
        except AttributeError:
            if name in ("__members__", "__methods__"):
                raise AttributeError()
            method = MockMethod(self, name, self._is_print)
            self._methods.append(method)
            return method

    def _get_mock_object_(self):
        mock_object = MockObject(self._is_print)
        mock_object._methods = [method.copy() for method in self._methods]
        return mock_object


class MockObject(object):
    def __init__(self, is_print = False):
        self._is_print = is_print
        self._methods = []
        self._current = 0

    def __getattribute__(self, name):
        try:
            attr = super(MockObject, self).__getattribute__(name)
            return attr
        except AttributeError:
            if name in ("__members__", "__methods__"):
                raise AttributeError()
            if len(self._methods) <= self._current:
                raise AssertionError("Mock: unexpected method call '%s'" % name)
            result = self._methods[self._current]
            self._current += 1
            return result.call(name)

    def _verify_(self):
        if len(self._methods) != self._current:
            raise AssertionError("Mock: method %s() must be called."
                                  % self._methods[self._current].name)
        if config.runtime.report_out:
            msg = ["MockObject should be call like this:"]
            if self._is_print:
                for method in self._methods:
                    msg.append(str(method))
                config.runtime.report_out.write((None, "\n".join(msg)))


class MockFile(object):
    def __init__(self, contents):
        self._contents = contents
        self._cursor = 0

    def write(self, actual):
        length = len(actual)
        start = self._cursor
        end = length + self._cursor
        try:
            expected = self._contents[start:end]
        except IndexError:
            raise AssertionError("FileMock: last write('%s') is unexpected" % actual)
        if expected != actual:
            raise AssertionError("FileMock: expected is '%s', but was '%s'" % (expected, actual))
        self._cursor = end

    def _verify_(self):
        start = self._cursor
        remain = len(self._contents) - start
        if remain > 0:
            str = self._contents[start:start+7]
            if remain > 7:
                str = str + "..."
            raise AssertionError("FileMock: %d chars(%s) must be written." % (remain, str))


class MockSocket(object):
    def __init__(self, recv=None, send=None):
        self._send_messages = []
        self._recv_messages = []
        self._blocking = 1
        self._timeout = None

        if type(recv) == str:
            self._add_recv_message_(recv)
        elif type(recv) in (list, tuple):
            self._add_recv_message_(*recv)
        if type(send) == str:
            self._add_send_message_(send)
        elif type(send) in (list, tuple):
            self._add_send_message_(*send)

    def _add_recv_message_(self, *message):
        self._recv_messages += list(message)

    def _add_send_message_(self, *message):
        self._send_messages += list(message)

    def recv(self, bufsize, flag=None):
        import socket, errno
        try:
            result = self._recv_messages[0]
            if len(result) > bufsize:
                self._recv_messages[0] = result[bufsize:]
                result = result[:bufsize]
            else:
                del self._recv_messages[0]
            return result
        except IndexError:
            if self._blocking == 1:
                raise AssertionError("recv buffer underflow")
            else:
                raise socket.error((errno.ETIMEDOUT, "timeout"))

    def send(self, string, flag=None):
        try:
            if self._send_messages[0] != string:
                raise AssertionError('MockSocket.send(): expected is "%s", but was "%s"' % (self._send_messages[0], string))
            del self._send_messages[0]
            return len(string)
        except IndexError:
            raise AssertionError('MockSocket.send(): unexpected send "%s"' % string)

    def accept(self):
        return (self, None)

    def setblocking(self, flag):
        if flag == 0:
            self.settimeout(0)
        else:
            self.settimeout(1)

    def settimeout(self, value):
        if value is None:
            self._blocking = 1
            self._timeout = None
        else:
            self._blocking = 0
            self._timeout = float(value)

    def gettimeout(self):
        return self._timeout

    def __getattribute__(self, name):
        try:
            attr = super(MockSocket, self).__getattribute__(name)
            return attr
        except AttributeError:
            if name in ["accept", "bind", "close", "connect", "connect_ex",
                        "fileno", "getpeername", "getsockname", "getsockopt",
                        "listen", "makefile", "recvfrom", "sendall", "sendto",
                        "setsockopt", "shutdown"]:
                return MockMethod(None, name)
            raise AttributeError(name)
