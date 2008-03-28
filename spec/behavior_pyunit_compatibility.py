# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework as framework
import unittest
import random


class SpecTestTrigger_PyUnit_Compatibility_Behavior(object):
    class SimpleTest(unittest.TestCase):
        def test_sum(self):
            def sum(a, b):
                return a + b
            self.assertEqual(sum(1, 3), 4)

        def test_mul(self):
            def mul(a, b):
                return a * b
            self.assert_(mul(2, 4) == 8)

    @spec
    def SpecTestTrigger_should_find_test_methods(self):
        fixture = self.SimpleTest
        test_trigger = framework.SpecTestTrigger(self.SimpleTest)
        test_trigger.run()
        About(len(test_trigger)).should_equal(2)

    class TestSequenceFunctions(unittest.TestCase):
        """Test Class for random module.

        This Code comes from Python Library Reference.
        """
        def setUp(self):
            self.seq = range(10)

        def testshuffle(self):
            random.shuffle(self.seq)
            self.seq.sort()
            self.assertEqual(self.seq, range(10))

        def testchoice(self):
            element = random.choice(self.seq)
            self.assert_(element in self.seq)

    @spec
    def SpecTestTrigger_should_run_tests_with_setUp(self):
        test_trigger = framework.SpecTestTrigger(self.TestSequenceFunctions)
        test_trigger.run()
        #print dir(fixture.testchoice)
        About(len(test_trigger)).should_equal(2)

    class PyUnitSequenceFixture(unittest.TestCase):
        def __init__(self, mock):
            self.mock = mock

        def setUp(self):
            self.mock.setUp()

        def test_method(self):
            self.mock.test_method()

        def tearDown(self):
            self.mock.tearDown()

    @context
    def SpecTestTrigger_with_pyunit(self):
        recorder = MockObjectRecorder(is_print=True)
        recorder.setUp()
        recorder.test_method()
        recorder.tearDown()
        self.mock = recorder._get_mock_object_()
        fixture = self.PyUnitSequenceFixture(self.mock)
        self.trigger = framework.SpecTestTrigger(fixture)

    @spec
    def should_run_context_and_finalize_methods(self):
        self.trigger.run()
        self.mock._verify_()


class PyUnitStyleTestCase_Success_Behavior(unittest.TestCase):
    def test_assertEqual(self):
        a = 10
        b = "hello"
        self.assertEqual(a, 10)
        self.assertEqual(b, "hello")

    def test_assertAlmostEqual(self):
        a = 10.1
        self.assertAlmostEqual(a, 10.2, 0.02)

    def test_assert(self):
        a = 10
        self.assert_(a == 10)

    def test_assertFalse(self):
        a = 11
        self.assertFalse(a == 10)

    def test_assertNotEqual(self):
        a = 10
        self.assertNotEqual(a, 11)

    def test_assertNotAlmostEqual(self):
        a = 10.1
        self.assertNotAlmostEqual(a, 11.0, 0.02)


if __name__ == "__main__":
    run_test()

