# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework
import socket


class MockMethod_Behavior(object):
    @context
    def a_MockMethod_object_whick_record_method_call(self):
        self.add = MockMethod(None, "add")
        self.add(1, 2) == 3
        self.add.is_recording = False

    @spec
    def knows_how_the_object_should_be_called(self):
        self.add(1, 2)

    @spec
    def knows_how_the_object_should_be_called(self):
        About(self.add(1, 2)).should_equal(3)


class MockObject_Behavior(object):
    @context
    def a_MockObject_object_which_record_method_call(self):
        recorder = MockObjectRecorder()
        recorder.add(1, 2) == 3
        self.mock = recorder._get_mock_object_()

    @spec
    def can_record_the_objects_behavior(self):
        About(self.mock.add(1, 2)).should_equal(3)

    @spec(expected=AssertionError)
    def can_find_unexpected_method_name(self):
        self.mock.mul(1, 2) # bad name

    @spec(expected=AssertionError)
    def can_find_unexpected_call(self):
        self.mock.add(1, 2)
        self.mock.add(1, 2) # bad call

    @spec(expected=AssertionError)
    def can_find_unexpected_method_argument(self):
        self.mock.add(2, 2) # bad args

    @spec(expected=AssertionError)
    def can_detect_that_expected_method_was_not_called(self):
        self.mock._verify_()    # add() is not called

    @spec
    def can_verify_all_expected_method_was_called(self):
        self.mock.add(1, 2)
        self.mock._verify_()


class MockObject_with_kwargs_Behavior(object):
    @context
    def a_MockObject_object_which_record_method_call_with_kwargs(self):
        recorder = MockObjectRecorder()
        recorder.add(first=1, second=2)
        self.mock = recorder._get_mock_object_()

    @spec(expected=AssertionError)
    def can_find_unexpected_method_keyword_argument(self):
        self.mock.add(first=2, second=2) # bad kwargs


class MockObject_with_repeated_call(object):
    @context
    def a_MockObject_object_which_record_repeated_method_call(self):
        recorder = MockObjectRecorder()
        recorder.add(1, 2).repeat(10) == 3
        self.mock = recorder._get_mock_object_()

    @spec
    def can_be_called_same_method_calls(self):
        for i in xrange(10):
            About(self.mock.add(1, 2)).should_equal(3)
        self.mock._verify_()

    @spec(expected=AssertionError)
    def can_find_method_call_in_short(self):
        for i in xrange(9): # smaller than 10!
            About(self.mock.add(1, 2)).should_equal(3)
        self.mock._verify_()


class MockObject_with_any_parameter(object):
    @context
    def a_MockObject_object_which_can_accept_any_parameter(self):
        recorder = MockObjectRecorder()
        recorder.add().with_any_parameter() == 3
        self.mock = recorder._get_mock_object_()

    @spec
    def can_be_called_with_any_parameter(self):
        About(self.mock.add(1, 2)).should_equal(3)
        self.mock._verify_()


class MockFile_Behavior(object):
    @spec
    def MockFile_can_be_used_similar_to_file_object(object):
        contents = "ABCDEF"
        mock = MockFile(contents)
        mock.write("ABC")
        mock.write("DEF")

    @spec(expected=AssertionError)
    def MockFile_can_detect_unexpected_string_was_written(self):
        contents = "ABCDEF"
        mock = MockFile(contents)
        mock.write("XYZ") # bad contents

    @spec(expected=AssertionError)
    def MockFile_can_detect_that_expected_string_has_not_been_written_yet(self):
        contents = "ABCDEFGHI"
        mock = MockFile(contents)
        mock.write("ABC")
        mock._verify_() # "DEF" is not written

    @spec
    def MockFile_can_verify_that_all_expected_string_has_been_written(self):
        contents = "ABCDEF"
        mock = MockFile(contents)
        mock.write("ABC")
        mock.write("DEF")
        mock._verify_()


class MockSocket_recv_Behavior(object):
    @context(group=1)
    def a_MockSocket_object(self):
        self.socket = MockSocket(recv=["ABC", "DEF"])

    @spec(group=0)
    def MockSocket_can_add_recv_strings_except_constructor(self):
        socket = MockSocket()
        socket._add_recv_message_("ABC", "DEF")
        About(socket.recv(4096)).should_equal("ABC")
        About(socket.recv(4096)).should_equal("DEF")

    @spec(group=0)
    def MockSocket_can_emulate_recv_that_can_get_small_flagment(self):
        socket = MockSocket()
        socket._add_recv_message_("ABCDEF")
        About(socket.recv(3)).should_equal("ABC")
        About(socket.recv(3)).should_equal("DEF")

    @spec(group=1)
    def can_emulate_recv_function(self):
        About(self.socket.recv(4096)).should_equal("ABC")
        About(self.socket.recv(4096)).should_equal("DEF")

    @spec(group=0)
    def MockSocket_can_set_recv_string_at_init(self):
        socket = MockSocket(recv=["ABC", "DEF"])
        About(socket.recv(4096)).should_equal("ABC")
        About(socket.recv(4096)).should_equal("DEF")

    @spec(group=0)
    def MockSocket_can_set_recv_string_at_init2(self):
        socket = MockSocket(recv="ABCDEF")
        About(socket.recv(4096)).should_equal("ABCDEF")

    @spec(expected=AssertionError, group=1)
    def recv_should_assertion_error_in_blocking_mode(self):
        About(self.socket.recv(4096)).should_equal("ABC")
        About(self.socket.recv(4096)).should_equal("DEF")
        About(self.socket.recv(4096)).should_equal("")

    @spec(expected=socket.error, group=1)
    def recv_should_socket_error_in_nonblocking_mode(self):
        self.socket.setblocking(0)
        About(self.socket.recv(4096)).should_equal("ABC")
        About(self.socket.recv(4096)).should_equal("DEF")
        About(self.socket.recv(4096)).should_equal("")

class MockSocket_send_Behavior(object):
    @spec
    def MockSocket_can_emulate_send_function(self):
        socket = MockSocket()
        socket._add_send_message_("ABC", "DEF")
        About(socket.send("ABC")).should_equal(3)
        About(socket.send("DEF")).should_equal(3)

    @spec(expected=AssertionError)
    def MockSocket_can_set_send_string_except_init(self):
        socket = MockSocket()
        socket._add_send_message_("HELLO")
        socket.send("WORLD")

    @spec(expected=AssertionError)
    def MockSocket_can_detect_unexpected_send_call(self):
        socket = MockSocket()
        socket.send("HELLO")

    @spec
    def MockSocket_can_set_send_string_at_init(self):
        socket = MockSocket(send="ABCDEF")
        About(socket.send("ABCDEF")).should_equal(6)

    @spec
    def MockSocket_can_set_send_string_at_init2(self):
        socket = MockSocket(send=["ABC", "DEF"])
        About(socket.send("ABC")).should_equal(3)
        About(socket.send("DEF")).should_equal(3)


if __name__ == "__main__":
    import sys
    if "gui" in sys.argv or "-gui" in sys.argv:
        import pyspec.wxui.controller
        controller = pyspec.wxui.controller.WxPySpecController(0)
        controller.MainLoop()
    else:
        import pyspec
        pyspec.run_test()
