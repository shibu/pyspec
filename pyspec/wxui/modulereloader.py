# -*- coding: ascii -*-

__pyspec = 1

import pyspec.framework
import pyspec.pyspec_api
from behavior import SpecFormatter

class WxTestModule(object):
    __slots__ = ("testclasses", "methods", "filepath", "has_error", "module",
                 "test_result", "has_error", "tddtree", "bddtree", "tddnode",
                 "bddnode", "tests")
    def __init__(self, filepath, tddtree, bddtree):
        import os, sys
        self.filepath = filepath
        self.has_error = False
        self.module = None
        self.test_result = ""
        self.testclasses = []
        self.methods = []
        self.tddtree = tddtree
        self.bddtree = bddtree
        self.bddnode = None
        dirname = os.path.dirname(self.filepath)
        if dirname not in sys.path:
            sys.path.insert(0, dirname)
        root = self.tddtree.GetRootItem()
        self.tddnode = self.tddtree.AppendItem(root, self.name())
        self.load()

    def load(self):
        import imp
        try:
            self.module = imp.load_source(self.name(), self.filepath)
        except:
            self.has_error = True
        self.test_setting()
        self.spec_setting()

    def try_reload_if_fail(self):
        if self.has_error and self.module is None:
            self.has_error = False
            self.load()

    def is_BDD(self):
        result = False
        for testclass in self.testclasses:
            result = result or testclass.is_BDD()
        return result

    def reload(self, has_error, module):
        import sys
        self.tests = None
        self.has_error = has_error
        self.module = module
        self.tddtree.DeleteChildren(self.tddnode)
        self.test_setting()
        self.spec_setting()

    def set_error(self, error_messages):
        self.tddtree.DeleteChildren(self.tddnode)
        self.tests = None
        self.testclasses = []
        self.methods = []
        sep = "\n%s\n" % "-" * 50
        self.test_result = sep.join(error_messages)
        self.tddtree.SetItemImage(self.tddnode, 4)

    def test_setting(self):
        import sys, traceback
        if self.has_error:
            exctype, value, tb = sys.exc_info()
            self.test_result = ''.join(traceback.format_exception(exctype, value, tb))
            self.tddtree.SetItemImage(self.tddnode, 4)
            return
        self.tests = TestLoader()
        self.tests.load_from_module(self.module)
        self.tests.find_trigger(self.module)
        self.test_result = ""
        self.load_child()
        self.tddtree.SetItemImage(self.tddnode, 0)

    def spec_setting(self):
        if self.is_BDD():
            if self.bddnode is None:
                root = self.bddtree.GetRootItem()
                self.bddnode = self.bddtree.AppendItem(root, self.name())
                self.bddtree.SetItemImage(self.bddnode, 5)
            else:
                self.bddtree.DeleteChildren(self.bddnode)
            for testclass in self.testclasses:
                testclass.regist_bdd(self.bddtree)
            self.bddtree.Expand(self.bddnode)
        else:
            self.bddtree = None

    def load_child(self):
        self.testclasses = []
        self.methods = []
        for test in self.tests.triggers:
            if test.target is self.module:
                for method in test.testmethods:
                    self.methods.append(WxTestMethod(self.tddtree, self, method))
            else:
                testclass = WxTestClass(self.tddtree, self, test)
                self.testclasses.append(testclass)
        self.tddtree.Expand(self.tddnode)

    def name(self):
        import os
        filename = os.path.split(self.filepath)[1]
        return os.path.splitext(filename)[0]

    def __len__(self):
        length = len(self.methods)
        for test in self.testclasses:
            length = length + len(test)
        return length

    def getmtime(self):
        import os
        return os.path.getmtime(self.module.__file__)

    def add_phases(self, result, selections):
        if self.tddnode in selections:
            selections = None
        for testclass in self.testclasses:
            testclass.add_phases(result, selections)
        for method in self.methods:
            method.add_phases(result, selections)

class WxTestClass(object):
    __slots__ = ("trigger", "methods", "module", "tddnode", "bddnode")
    def __init__(self, tddtree, parent, trigger):
        self.trigger = trigger
        self.methods = []
        self.module = parent
        self.tddnode = tddtree.AppendItem(parent.tddnode, self.name())
        self.bddnode = None
        for method in trigger.testmethods:
            self.methods.append(WxTestMethod(tddtree, self, method))

    def is_BDD(self):
        result = False
        for method in self.methods:
            result = result or method.is_BDD()
        return result

    def regist_bdd(self, bddtree):
        if not self.is_BDD():
            self.bddnode = None
            return
        self.bddnode = bddtree.AppendItem(self.module.bddnode, self.name())
        bddtree.SetItemImage(self.bddnode, 5)

    def name(self):
        return self.trigger.target.__class__.__name__

    def description(self):
        import inspect
        result = inspect.getdoc(self.trigger.target)
        return result

    def __len__(self):
        return len(self.methods)

    def print_spec(self, htmlview):
        formatter = SpecFormatter(self)
        html = formatter.create_html()
        htmlview.SetPage(html)

    def add_phases(self, result, selections):
        if (selections is not None) and self.tddnode in selections:
            selections = None
        for method in self.methods:
            method.add_phases(result, selections)

class WxTestMethod(object):
    __slots__ = ("parent", "method", "tddnode", "test_result", "console", "bddreport")
    def __init__(self, tddtree, parent, method):
        self.parent = parent
        self.method = method
        self.tddnode = tddtree.AppendItem(parent.tddnode, self.name())
        self.test_result = ""
        self.bddreport = []
        self.console = []

    def report(self, report):
        self.bddreport = report

    def is_BDD(self):
        attr = getattr(self.method, "__unittest_attribute")
        return attr.is_BDD

    def BDD_ok(self):
        result = True
        for report in self.bddreport:
            result = result and report[0]
        return result

    def context_checker(self):
        attr = getattr(self.method, "__unittest_attribute")
        return attr.use_context

    def set_test_result(self, message):
        self.test_result = message

    def name(self):
        return self.method.__name__

    def long_name(self):
        attr = getattr(self.method, "__unittest_attribute")
        return str(attr)

    def module_mtime(self):
        if isinstance(self.parent, WxTestClass):
            return self.parent.module.getmtime()
        return self.parent.getmtime()

    def get_id(self):
        attr = getattr(self.method, "__unittest_attribute")
        return id(attr)

    def add_phases(self, result, selections):
        if selections is None:
            select = True
        elif self.tddnode in selections:
            select = True
        else:
            select = False
        if select:
            result.update(set(self.phases))
