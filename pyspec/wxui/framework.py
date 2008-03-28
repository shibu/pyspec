# -*- coding: ascii -*-

__pyspec = 1

import os
import threading

import pyspec.api
import pyspec.util
import pyspec.reloader
import pyspec.framework
import pyspec.wxui.project
from pyspec.wxui.const import *


class NoTestCaseNotifier(Exception):
    pass


class ModuleTreeNode(pyspec.api.ModuleAspect):
    __slots__ = pyspec.api.ModuleAspect.__slots__ + \
                ('spec_explorer', 'treenode')
    def __init__(self, observer):
        super(ModuleTreeNode, self).__init__(observer)
        self.tree = None
        self.treenode = None

    def init(self, viewer):
        self.tree = viewer.spec_explorer
        test_module = self.find_aspect("pyspec")
        if test_module.is_spectest():
            root = self.tree.GetRootItem()
            spec_name = test_module.spec_name(long=True)
            node = self.tree.AppendItem(root, spec_name)
            self.tree.SetItemImage(node, RT_NOT_RUN)
            self.treenode = node
            for classobj in self.classes(sort_by=pyspec.util.sort_by_index):
                classobj.init(viewer, self.treenode)
            for method in self.methods(sort_by=pyspec.util.sort_by_index):
                method.init(viewer, self.treenode)
            if viewer.view_mode != VIEW_RT_ALL:
                if not self.tree.ItemHasChildren(node):
                    self.tree.Delete(node)
                    self.treenode = None
                else:
                    self.tree.Expand(node)
            else:
                self.tree.Expand(node)

    def set_error(self, error_messages):
        self.tree.DeleteChildren(self.treenode)
        self.tests = None
        sep = "\n%s\n" % "-" * 50
        pyspecmodule = self.find_aspect("pyspec")
        pyspecmodule.test_result = sep.join(error_messages)
        self.tree.SetItemImage(self.treenode, RT_ERROR)

    def test_setting(self):
        pyspecmodule = self.find_aspect("pyspec")
        if self.has_error:
            exctype, value, tb = sys.exc_info()
            pyspecmodule.test_result = ''.join(traceback.format_exception(
                                                         exctype, value, tb))
            self.tree.SetItemImage(self.treenode, RT_LOAD_FAIL)
        else:
            self.tests = TestLoader()
            self.tests.load_from_module(self.module)
            self.tests.find_trigger(self.module)
            pyspecmodule.test_result = ""
            self.load_child()
            self.tree.SetItemImage(self.treenode, RT_NOT_RUN)


class ClassTreeNode(pyspec.api.ClassAspect):
    __slots__ = pyspec.api.ClassAspect.__slots__ + ('treenode',)
    def __init__(self, observer):
        super(ClassTreeNode, self).__init__(observer)
        self.treenode = None

    def init(self, viewer, parent):
        specaspect = self.find_aspect("pyspec")
        tree = viewer.spec_explorer
        if specaspect.is_spectest():
            self.treenode = tree.AppendItem(parent, specaspect.spec_name())
            tree.SetItemImage(self.treenode, RT_NOT_RUN)
            for method in self.methods(sort_by=pyspec.util.sort_by_index):
                method.init(viewer, self.treenode)
            if viewer.view_mode != VIEW_RT_ALL:
                if not tree.ItemHasChildren(self.treenode):
                    tree.Delete(self.treenode)
                    self.treenode = None
                else:
                    tree.Expand(self.treenode)

    def description(self):
        return self.find_aspect("pyspec").description()


class MethodTreeNode(pyspec.api.MethodAspect):
    __slots__ = pyspec.api.MethodAspect.__slots__ + ('treenode', 'bddreport',
                                                     'result_type')
    def __init__(self, observer):
        super(MethodTreeNode, self).__init__(observer)
        self.treenode = None
        self.result_type = RT_NOT_RUN

    def init(self, viewer, parent_node):
        test_method = self.find_aspect("pyspec")
        tree = viewer.spec_explorer
        if test_method.is_spectest:
            if self.result_type in viewer.view_mode:
                self.treenode = tree.AppendItem(parent_node,
                                                test_method.spec_name())
                tree.SetItemImage(self.treenode, self.result_type)
                if self.result_type != RT_NOT_RUN:
                    viewer.set_parent_icon(self.treenode)

    def report(self, report):
        self.bddreport = report


class WxSpecTester(object):
    def __init__(self):
        self.kernel = pyspec.framework.PySpecKernel()
        self.spec_modules = []
        self.selected = []
        self.project = pyspec.wxui.project.WxPySpecProjectManager()
        self.load_lock = threading.RLock()

    def init_check(self, viewer):
        self.kernel.modules.add_listener("spec_tree_node", ModuleTreeNode,
                                         ClassTreeNode, MethodTreeNode, viewer)
        self.kernel.modules.load_all()
        for filepath in self.project.get_modules():
            self.append(filepath, from_file=True)

    def recreate_tree(self, viewer):
        self.kernel.modules.send_all("spec_tree_node", "init", viewer)

    def open(self, spec_explorer, filename = None):
        try:
            self.load_lock.acquire()
            try:
                self.project.open(filename)
                for filepath in self.project.get_modules():
                    self.append(filepath)
            except IOError:
                pass
        finally:
            self.load_lock.release()

    def save(self, filename = None):
        filelist = [module.observer.path for module in self.spec_modules]
        self.project.set_modules(filelist)
        if filename is not None:
            self.project.save_as(filename)
        else:
            self.project.save()

    def clear_all(self, treectrl):
        for testmodule in self.spec_modules:
            treectrl.Delete(testmodule.find_aspect("spec_tree_node").treenode)
            self.kernel.modules.remove_module(testmodule)
        self.spec_modules = []
        self.selected = []

    def check_loaded_modules(self):
        try:
            self.load_lock.acquire()
            #return self.module_reloader.check_loaded_modules(self.spec_modules)
        finally:
            self.load_lock.release()

    def update(self):
        try:
            self.load_lock.acquire()
            return self.module_reloader.update(self.spec_modules)
        finally:
            self.load_lock.release()

    def append(self, path, from_file=False):
        try:
            self.load_lock.acquire()
            module = self.kernel.modules.load_module(path)
            if module is None:
                return None
            spec_module = module.find_aspect("pyspec")
            if len(spec_module) == 0 and not spec_module.has_error:
                return None
            self.spec_modules.append(spec_module)
            if not from_file:
                self.project.set_dirty_flag()
            return spec_module
        finally:
            self.load_lock.release()

    def delete(self, module_name, treectrl):
        for i in xrange(len(self.spec_modules)):
            testmodule = self.spec_modules[i]
            if testmodule.name() == module_name:
                treenode = testmodule.find_aspect("spec_tree_node").treenode
                treectrl.Delete(treenode)
                del self.spec_modules[i]
        self.project.set_dirty_flag()

    def search_dir(self, path, spec_explorer, bddtree):
        try:
            self.load_lock.acquire()
            count = 0
            for name in os.listdir(path):
                fullpath = os.path.abspath(name)
                if os.path.isfile(fullpath) and fullpath.endswith(".py"):
                    result = self.append(fullpath, spec_explorer, bddtree)
                    if result is not None:
                        count = count + 1
            return count
        finally:
            self.load_lock.release()

    def run(self, result):
        self.kernel.clear_callstack()
        try:
            self.load_lock.acquire()
            for module in self.selected:
                module.run(result)
        finally:
            self.load_lock.release()

    def find_spec_print_class(self, bddnode, htmlview):
        for testmodule in self.spec_modules:
            if testmodule.bddnode == bddnode:
                htmlview.SetPage("<HTML><BODY></BODY></HTML>")
                return
            for testclass in testmodule.testclasses:
                if testclass.bddnode == bddnode:
                    testclass.print_spec(htmlview)
                    return

    def selected_method_phases(self, selections):
        result = set()
        for testmodule in self.spec_modules:
            testmodule.add_phases(result, selections)
        return result

    def select_all(self):
        self.selected = []
        for test_module in self.kernel.modules.get_modules("pyspec"):
            if len(test_module) > 0:
                self.selected.append(TestList(test_module, is_all=True))

    def find_tests(self, selections):
        """maybe I can refactor by module_observer functions"""
        self.selected = []
        table = {}
        for module in self.spec_modules:
            treenode = module.find_aspect("spec_tree_node").treenode
            if treenode in selections:
                testlist = TestList(module, is_all=True)
                table[id(module)] = testlist
                self.selected.append(testlist)
                #print module.name()
            else:
                for method in module.methods():
                    treenode = method.find_aspect("spec_tree_node").treenode
                    if treenode in selections:
                        #print method.name()
                        try:
                            table[id(module)].methods.append(method)
                        except KeyError:
                            testlist = TestList(module)
                            testlist.methods.append(method)
                            self.selected.append(testlist)
                            table[id(module)] = testlist
                for classobj in module.classes():
                    treenode = classobj.find_aspect("spec_tree_node").treenode
                    if treenode in selections:
                        testlist = TestList(classobj, is_all=True)
                        testlist.is_class = True
                        table[id(classobj)] = testlist
                        self.selected.append(testlist)
                        #print testclass.name()
                    else:
                        for method in testclass.methods():
                            treenode = method.find_aspect("spec_tree_node").treenode
                            if treenode in selections:
                                #print method.name()
                                try:
                                    table[id(testclass)].methods.append(method)
                                except KeyError:
                                    testlist = TestList(testclass)
                                    testlist.is_class = True
                                    testlist.methods.append(method)
                                    self.selected.append(testlist)
                                    table[id(testclass)] = testlist

    def __len__(self):
        result = 0
        for testlist in self.selected:
            if testlist.is_all:
                result = result + len(testlist.module)
            else:
                result = result + len(testlist.methods)
        return result

    def get_all_test_count(self):
        result = 0
        for testmodule in self.kernel.modules.get_modules("pyspec"):
            result = result + len(testmodule)
        return result



class TestList(object):
    def __init__(self, module, is_all=False):
        self.module = module
        self.is_all = is_all
        self.is_class = False
        self.methods = []

    def run(self, result):
        if self.is_class and self.module is not None:
            if self.is_all:
                self.module.trigger.run(result)
            else:
                self.module.trigger.run(result, self.method_list())
        else:
            trigger = self.module.trigger
            if self.is_all:
                if trigger is not None:
                    trigger.run(result)
                for testclass in self.module.classes():
                    if testclass.trigger is not None:
                        testclass.trigger.run(result)
            else:
                trigger.run(result, self.method_list())

    def method_list(self):
        return [test_method.method for test_method in self.methods]


class WxSpecResultRecorder(pyspec.framework.SpecResultRecorder):
    def __init__(self, viewer, number_of_tests):
        super(WxSpecResultRecorder, self).__init__()
        self.number_of_tests = number_of_tests
        self.viewer = viewer
        self.viewer.init_progressbar_range(self.number_of_tests)
        self.failure_methods = []
        self.success_methods = []
        self.ignored_methods = []

    def get_description(self, test):
        if self.test_results:
            return test.short_description() or str(test)
        else:
            return str(test)

    def start_test(self, test, contexts, data_args=None):
        super(WxSpecResultRecorder, self).start_test(test, contexts, data_args)
        if data_args:
            append_text = " <args=%s>" % " ".join(
                ("%s:%s" % (key, value) for key, value in data_args.iteritems()))
        else:
            append_text = ""
        self.viewer.print_status("running '%s%s'" % (str(test), append_text))

    def stop_test(self, test):
        super(WxSpecResultRecorder, self).stop_test(test)
        self.viewer.print_testresult_count(self)

    def _set_result_type(self, test, result_type):
        treenode = test.find_aspect("spec_tree_node")
        treenode.result_type = result_type

    def _add_failure_or_error(self, test, err, error_type):
        self._set_result_type(test, error_type)
        test.test_result = pyspec.util.exc_info_to_string(err)
        self.failure_methods.append(test)
        self.viewer.print_error_and_failure(self, test, err)

    def add_success(self, test):
        super(WxSpecResultRecorder, self).add_success(test)
        self._set_result_type(test, RT_SUCCESS)
        test.test_result = "OK"
        self.success_methods.append(test)
        self.viewer.print_success(self, test)

    def add_error(self, test, err):
        super(WxSpecResultRecorder, self).add_error(test, err)
        self._add_failure_or_error(test, err, RT_ERROR)

    def add_failure(self, test, err):
        super(WxSpecResultRecorder, self).add_failure(test, err)
        self._add_failure_or_error(test, err, RT_FAILURE)

    def add_ignore(self, test):
        super(WxSpecResultRecorder, self).add_ignore(test)
        test.test_result = "Ignored"
        self._set_result_type(test, RT_IGNORED)
        self.ignored_methods.append(test)
        self.viewer.print_ignore(self, test)
