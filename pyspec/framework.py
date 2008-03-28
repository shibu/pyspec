# -*- coding: ascii -*-

"""PySpec framework core classes.
"""

import re
import os
import sys
import types
import traceback
import inspect
import unittest
import pyspec
import pyspec.util as util
import pyspec.api
import pyspec.modulebrowser
import pyspec.compat_ironpython
import pyspec.embedded.dbc as dbc
from pyspec.embedded.setting import config
language = config.language


__pyspec = 1


class PySpecKernel(object):
    """PySpec kernel that manage modules."""
    def __init__(self):
        self.modules = pyspec.modulebrowser.ModuleBrowser()
        self.modules.add_listener("pyspec", SpecModule, SpecClass, SpecMethod)

    def set_all_modules(self):
        self.modules.load_all()

    def clear_callstack(self):
        for module in self.modules.get_modules("pyspec"):
            for function in module.functions():
                function.stack = []
            for classobj in module.classes():
                for method in classobj.methods():
                    method.stack = []


class SpecTestTrigger(object):
    """Run spec test and setup, teardown methods.
    This class is a bese class of SpecModule, SpecClass.
    """
    def __init__(self, target_object, runtime_option=None):
        self.target_object = target_object
        self.is_spectest = False
        self.is_init = False
        self.is_pyunit = True
        self.data_providers = []
        self.context_methods = []
        self.spec_methods = []
        self.finalize_methods = []
        self.runtime_option = runtime_option

    def __len__(self):
        """Return test count."""
        return len(self.spec_methods)

    def _is_pyunit(self):
        if isinstance(self.target_object, unittest.TestCase):
            return True
        if isinstance(self.target_object, (types.ClassType, types.TypeType)):
            if issubclass(self.target_object, unittest.TestCase):
                return True
        return False

    def search_method(self, methods):
        """create test trigger from test class, test module.

        This method categorize all methods of target to specs,
        contexts, finalizes. Each list is sorted by the order
        of definition.

        @category init.create_trigger
        """
        if self._is_pyunit():
            self._search_method_for_pyunit(methods)
        else:
            self._search_method_for_pyspec(methods)

        self.spec_methods.sort(cmp=lambda x, y: cmp(x.index(), y.index()))
        self.context_methods.sort(cmp=lambda x, y: cmp(x.index(), y.index()))
        self.finalize_methods.sort(cmp=lambda x, y: cmp(x.index(), y.index()))
        self.data_providers.sort(cmp=lambda x, y: cmp(x.index(), y.index()))
        self.is_spectest = (len(self.spec_methods) > 0) or self.is_spectest
        self.is_init = True

    def _search_method_for_pyspec(self, methods):
        #print "_search_method_for_pyspec()"
        for method in methods:
            #print method.short_name()
            if method.is_spectest:
                self.spec_methods.append(method)
            elif method.is_context():
                self.context_methods.append(method)
            elif method.is_finalize():
                self.finalize_methods.append(method)
            elif method.is_data_provider():
                self.data_providers.append(method)

    def _search_method_for_pyunit(self, methods):
        for method in methods:
            if method.short_name() == "setUp":
                self.context_methods.append(method)
                method.init_as_pyunit_context()
            elif method.short_name() == "tearDown":
                self.finalize_methods.append(method)
                method.init_as_pyunit_finalize()
            elif method.short_name().startswith("test"):
                self.spec_methods.append(method)
                method.init_as_pyunit_spec()

    def _init_method_for_test(self):
        """Create test trigger from test class, for pyspec tests.
        Create dummy observer(not registered pyspec.modulebrowser.ModuleBrowser).
        """
        #print "_init_method_for_test"
        observer = pyspec.modulebrowser.ClassObserver("", self.target_object, None)
        observer.add_listener(("pyspec", None, SpecClass, SpecMethod, []))
        aspect, spec_class = observer[0]
        spec_class.init()
        self.search_method(spec_class.methods())

    def _context(self, fixture, spec_method, is_first):
        """execute context method.
        @category exec.module.context_methods
        """
        check_docstring = config.framework.check_docstring
        if is_first:
            for context in self.context_methods:
                if context.attribute.is_class:
                    #print "run %s" % context_method.name()
                    if check_docstring and context.target().__doc__ is None:
                        raise AssertionError("context method must have docstring.")
                    context.attribute.context(fixture, context)

        for context in self.context_methods:
            if not context.attribute.is_class and spec_method.in_same_group(context):
                if check_docstring and context.target().__doc__ is None:
                    raise AssertionError("context method must have docstring.")
                context.attribute.context(fixture, context)
            #remove comment, print pass method names
            #elif not attr.is_class:
            #    print "not run %s" % context_method.name()

    def _collect_context(self, spec_method):
        result = []
        for context in self.context_methods:
            if not context.attribute.is_class and spec_method.in_same_group(context):
                result.append(context)
        if len(result) == 0:
            return None
        return result

    def _collect_test_data(self, spec_method):
        input_values = [data_provider.generate_test_data()
                           for data_provider in self.data_providers
                           if spec_method.in_same_group(data_provider)]
        return _direct_product_test_data(input_values)

    def _finalize(self, fixture, is_last, is_finalizeclass_only=False):
        """execute finalize method.
        @category exec.module.finalize_methods
        """
        if not is_finalizeclass_only:
            for finalizer in self.finalize_methods:
                if not finalizer.attribute.is_class:
                    print "run %s" % finalizer.name()
                    finalizer.attribute.finalize(fixture, finalizer)
        if is_last:
            for finalizer in self.finalize_methods:
                if finalizer.attribute.is_class:
                    print "run %s" % finalizer.name()
                    finalizer.attribute.finalize(fixture, finalizer)

    def run(self, recorder=None, methodlist=None):
        """execute test methods.
        @category exec.module
        """
        if not self.is_init:
            self._init_method_for_test()
        if recorder is None:
            recorder = DummyResultRecorder()

        for i, spec_method in enumerate(self.spec_methods):
            is_first = (i == 0)
            is_last = (i == len(self.spec_methods) -1)
            if recorder is not None and recorder.should_stop:
                break
            if methodlist is not None:
                if not spec_method in methodlist:
                    return
            contexts = self._collect_context(spec_method)
            spec_method.regist_contexts_names(contexts)
            if spec_method.attribute.ignored:
                recorder.start_test(spec_method, contexts)
                recorder.add_ignore(spec_method)
                recorder.stop_test(spec_method)
                continue
            try:
                data_args_list = self._collect_test_data(spec_method)
            except ValueError:
                recorder.start_test(spec_method, contexts, [])
                recorder.add_error(spec_method, sys.exc_info())
                recorder.stop_test(spec_method)
                continue
            for data_args in data_args_list:
                #print "data_args:", data_args
                recorder.start_test(spec_method, contexts, data_args)
                config.runtime.start_spec("%s<%s>" %
                    (spec_method.short_name(), str(data_args)))
                fixture = spec_method.get_fixture()
                if spec_method.use_dbc():
                    dbc.set_dbc_option(prepost=True, invariant=True)
                try:
                    if self.runtime_option:
                        config.regist_config("runtime", self.runtime_option)
                    try:
                        self._context(fixture, spec_method, is_first)
                    except:
                        recorder.add_error(spec_method, sys.exc_info())
                        try:
                            self._finalize(fixture, is_last, True)
                        except:
                            pass
                        continue
                    try:
                        if spec_method.run(fixture, recorder, data_args):
                            recorder.add_success(spec_method)
                    finally:
                        self._finalize(fixture, is_last)
                finally:
                    if self.runtime_option:
                        config.remove_config("runtime")
                    recorder.stop_test(spec_method)
                    if spec_method.use_dbc():
                        dbc.set_dbc_option(prepost=False, invariant=False)
        return recorder

    def lowest_index(self):
        if self.spec_methods:
            return self.spec_methods[0].index()
        return 0


class SpecBase(object):
    def short_name(self):
        if self.target().__name__ == "":
            return self.name()
        return self.target().__name__

    def short_description(self):
        """Returns a one-line description of the test.
        return None if no description has been provided.
        """
        module = self.module()
        if module is None:
            return ""
        doc = module.decode(self.target().__doc__)
        return doc and doc.split("\n")[0].strip() or None

    def description(self):
        return self.module().decode(self.target().__doc__)

    def spec_name(self, long=False):
        name = self.short_description()
        if name is None:
            name = util.create_spec_name(self.short_name())
        elif long:
            name = "%s (%s)" % (name, str(self))
        return name


class SpecModule(pyspec.api.ModuleAspect, SpecBase):
    __slots__ = pyspec.api.ModuleAspect.__slots__ + ('trigger', 'test_result')
    def __init__(self, observer):
        super(SpecModule, self).__init__(observer)
        self.trigger = SpecTestTrigger(observer.target)
        self.test_result = ''
        self.codec = None
        try:
            sourcecode = inspect.getsourcelines(observer.target)[0][0]
            match = re.search(r"# -\*- (?P<codec>.*) -\*-", sourcecode)
            if match:
                self.codec = match.group("codec").split()[-1]
        except IOError:
            pass

    def init(self):
        for classobj in self.classes():
            classobj.init()
        for method in self.methods():
            method.init()
        self.trigger.search_method(self.methods())
        if len(self.trigger) == 0:
            self.trigger = None

    def is_spectest(self):
        if self.trigger is None:
            result = False
        else:
            result = self.trigger.is_spectest
        for classobj in self.classes():
            result = classobj.is_spectest() or result
        return result

    def run(self, recorder=None, methodlist=None):
        config.runtime.module_name = self.short_name()
        classlist = self.classes()
        classlist.sort(cmp=lambda x, y: cmp(x.index(), y.index()))
        for classobj in classlist:
            classobj.run(recorder, methodlist)
        config.runtime.class_name = None
        if self.trigger is not None:
            self.trigger.run(recorder, methodlist)

    def __len__(self):
        """Return test count."""
        count = 0
        if self.trigger is not None:
            count = len(self.trigger)
        for classobj in self.classes():
            count = count + len(classobj)
        return count

    def decode(self, str):
        if self.codec is None or str is None:
            return str
        return str.decode(self.codec)


class SpecClass(pyspec.api.ClassAspect, SpecBase):
    __slots__ = pyspec.api.ClassAspect.__slots__ + ('trigger',)
    def __init__(self, observer):
        """Init class observer.
        self.trigger is None, if this class is not test class.
        """
        super(SpecClass, self).__init__(observer)
        self.trigger = SpecTestTrigger(observer.target)

    def init(self):
        for method in self.methods():
            method.init()
        self.trigger.search_method(self.methods())
        if len(self.trigger) == 0:
            self.trigger = None

    def run(self, recorder=None, methodlist=None):
        if self.trigger is not None:
            config.runtime.class_name = self.short_name()
            self.trigger.run(recorder, methodlist)

    def is_spectest(self):
        if self.trigger is None:
            return False
        return self.trigger.is_spectest

    def __len__(self):
        """Return test count."""
        if self.trigger is None:
            return 0
        return len(self.trigger)

    def index(self):
        if self.trigger is not None:
           self.trigger.lowest_index()
        return 0


class SpecMethod(pyspec.api.MethodAspect, SpecBase):
    __slots__ = pyspec.api.MethodAspect.__slots__ + \
                ('is_spectest', 'console', 'stack',
                 'coverage', 'is_print', 'is_debugger',
                 'test_result', 'ignore_trace', 'contexts')
    dispatch = {
        "call": 0,
        "exception": 1,
        "return": 2,
        "c_call": 3,
        "c_exception": 4,
        "c_return": 5,
        "line": 6}

    def __init__(self, observer):
        super(SpecMethod, self).__init__(observer)
        self.is_spectest = False
        self.console = []
        self.stack = []
        self.coverage = set()
        self.is_print = False
        self.is_debugger = False
        self.test_result = ""
        self.ignore_trace = False
        self.attribute = None
        self.contexts = []

    def id(self):
        return id(self.target())

    def __str__(self):
        if self.parent() == self.module():
            return "%s:%s()" % (self.parent().target().__name__,
                              self.target().__name__)
        else:
            return "%s:%s.%s()" % (self.module().target().__name__,
                                 self.parent().target().__name__,
                                 self.target().__name__)
        return self.name

    def init(self):
        self.attribute = getattr(self.target(), "__pyspec_attribute", None)
        if isinstance(self.attribute, pyspec.SpecMethodAttribute):
            self.is_spectest = True
        if hasattr(self.parent().observer, "test_class"):
            self.ignore_trace = self.parent().observer.test_class
        elif self.module().is_system():
            self.ignore_trace = True

    def init_as_pyunit_spec(self):
        self.attribute = pyspec.SpecMethodAttribute()
        self.is_spectest = True

    def init_as_pyunit_context(self):
        self.attribute = pyspec.ContextMethodAttribute()

    def init_as_pyunit_finalize(self):
        self.attribute = pyspec.FinalizeMethodAttribute()

    def trace_dispatch(self, frame, event, arg):
        if config.runtime.ignore_stack or self.ignore_trace:
            return
        code = self.dispatch[event]
        if code == 6:
            self.coverage.add((frame.f_code.co_filename, frame.f_lineno))
        else:
            stack_frame = util.IsolatedStackFrame(code, frame, arg)
            self.stack.append(stack_frame)
        #print event, methodinfo
        if code in [0, 1, 6]:
            return self.trace_dispatch

    def get_fixture(self):
        """Return spec class's instance.

        if self.target have an instance or a module, return that.
        if self.target is Type or Class, return instance of that.
        """
        method = self.target()
        if type(method) is types.UnboundMethodType:
            parent = self.parent().target()
            if isinstance(parent, (types.ClassType, types.TypeType)):
                if issubclass(parent, unittest.TestCase):
                    return parent(self.short_name())
                return parent()
            else:
                return parent
        if type(method) is types.FunctionType:
            return self.parent().target()
        raise ValueError("Can't get fixture in %s" % self.short_name())

    def run(self, fixture, recorder, data_args):
        """Run test method."""
        if not self.is_spectest:
            return None
        self.stack = []
        method_name = self.target().__name__
        config.runtime.start_spec(method_name)
        spec_method = getattr(fixture, method_name)
        check_docstring = config.framework.check_docstring
        if check_docstring and spec_method.__doc__ is None:
            try:
                raise AssertionError("Spec method must have docstring.")
            except:
                if isinstance(recorder, DummyResultRecorder):
                    raise
                recorder.add_failure(self, sys.exc_info())
                return False
        if self.attribute.expected is not None:
            return self._run_spec_with_expected(recorder, spec_method, data_args)
        return self._run_spec(recorder, spec_method, data_args)

    def _run_spec_with_expected(self, recorder, spec_method, data_args):
        if self.is_debugger:
            sys.settrace(self.trace_dispatch)
        else:
            sys.setprofile(self.trace_dispatch)
        try:
            try:
                spec_method(**data_args)
                if config.runtime.recording_flag:
                    msg = language.get("framework", "record_legacy")
                    recorder.add_ignore(self, msg)
                    return False
            except self.attribute.expected:
                msg = language.get("framework", "expected",
                        expected_exception=self.attribute.expected.__name__)
                config.runtime.report_out.write((None, msg))
                return True
            except pyspec.IgnoreTestCase:
                recorder.add_ignore(self)
                if isinstance(recorder, DummyResultRecorder):
                    raise
            except KeyboardInterrupt:
                raise
            except:
                if config.environment.show_error:
                    traceback.print_exc()
                recorder.add_error(self, sys.exc_info())
            else:
                try:
                    msg = language.get("framework", "expected",
                           expected_exception=self.attribute.expected.__name__)
                    raise AssertionError(msg)
                except:
                    recorder.add_failure(self, sys.exc_info())
            return False
        finally:
            if sys.platform != "cli":
                if self.is_debugger:
                    sys.settrace(None)
                else:
                    sys.setprofile(None)
            if len(self.stack) > 1:
                self.stack = self.stack[1:-1]

    def _run_spec(self, recorder, spec_method, data_args):
        if self.is_debugger:
            sys.settrace(self.trace_dispatch)
        else:
            sys.setprofile(self.trace_dispatch)
        try:
            try:
                spec_method(**data_args)
                if config.runtime.recording_flag:
                    msg = language.get("framework", "record_legacy")
                    recorder.add_ignore(self, msg)
                    return False
            except AssertionError:
                if isinstance(recorder, DummyResultRecorder):
                    raise
                recorder.add_failure(self, sys.exc_info())
            except pyspec.IgnoreTestCase:
                if isinstance(recorder, DummyResultRecorder):
                    raise
                recorder.add_ignore(self)
            except KeyboardInterrupt:
                raise
            except:
                if config.environment.show_error:
                    traceback.print_exc()
                if isinstance(recorder, DummyResultRecorder):
                    raise
                recorder.add_error(self, sys.exc_info())
            else:
                return True
            return False
        finally:
            if sys.platform != "cli":
                if self.is_debugger:
                    sys.settrace(None)
                else:
                    sys.setprofile(None)
            if len(self.stack) > 1:
                self.stack = self.stack[1:-1]

    def is_context(self):
        if self.attribute is None:
            return False
        return self.attribute.is_context

    def is_finalize(self):
        if self.attribute is None:
            return False
        return self.attribute.is_finalize

    def is_data_provider(self):
        if self.attribute is None:
            return False
        return self.attribute.is_data_provider

    def console_out(self, id, s):
        self.console.append((id, s))

    def in_same_group(self, context_or_provider):
        if self.attribute.groups is None:
            return True
        result = context_or_provider.attribute.group in self.attribute.groups
        if result:
            if context_or_provider.attribute.is_context:
                name = "context: %s\n" % context_or_provider.spec_name()
                self.console.append((util.CONTEXT_INFO, name))
            elif context_or_provider.attribute.is_data_provider:
                name = "data_provider: %s\n" % context_or_provider.spec_name()
                self.console.append((util.DATA_PROVIDER_INFO, name))
        return result

    def index(self):
        if self.attribute is None:
            return 0
        if isinstance(self.attribute, pyspec.SpecMethodAttribute):
            return self.attribute.index
        return 0

    def spec_name(self, long=False, context=False):
        try:
            if context and issubclass(self.parent().target(), unittest.TestCase):
                return self.parent().spec_name(long)
        except TypeError:
            pass
        return super(SpecMethod, self).spec_name(long)

    def generate_test_data(self):
        data_provider = getattr(self.parent().target(), self.target().__name__)
        return (self.attribute.key, data_provider())

    def regist_contexts_names(self, contexts):
        if contexts is None:
            self.contexts = []
        else:
            self.contexts = [context.spec_name(context=True)
                                for context in contexts]

    def use_dbc(self):
        return self.attribute.dbc


class DummyResultRecorder(object):
    """Dummy TestResult class for testing itself"""
    def __init__(self):
        self.should_stop = False
        self.ignore_count = 0

    def add_ignore(self, *args):
        self.ignore_count += 1

    def dummy(self, *args):
        pass
    start_test = stop_test = add_error = add_failure = dummy
    add_success = stop = begin_test = finish_test = dummy


class SpecResultRecorder(object):
    """Holder for test result information.

    This class is based on pyspec (thank you!).
    """
    def __init__(self):
        """init test recorder.
        @category init.recorder
        """
        self.failures = []
        self.errors = []
        self.ignores = []
        self.run_count = 0
        self.should_stop = False

    def start_test(self, spec, contexts, data_args):
        "Called when the given test is about to be run"
        self.run_count = self.run_count + 1
        sys.stdout = util.ConsoleHook(spec, util.STDOUT,
                config.environment.show_error)
        sys.stderr = util.ConsoleHook(spec, util.STDERR,
                config.environment.show_error)
        config.runtime.report_out = util.ConsoleHook(spec, util.REPORT_OUT)
        spec.console = []

    def stop_test(self, test):
        "Called when the given test has been run"
        sys.stdout.reset_system_console()
        sys.stderr.reset_system_console()
        config.runtime.report_out = None

    def add_error(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        @category testcase.error
        """
        self.errors.append((test, util.exc_info_to_string(err)))

    def add_failure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        @category testcase.failure
        """
        self.failures.append((test, util.exc_info_to_string(err)))

    def add_ignore(self, test, message=None):
        """Called when an ignore test method called.
        @category testcase.ignore
        """
        self.ignores.append((test, message))

    def add_success(self, test):
        """Called when a test has completed successfully.
        @category testcase.success
        """
        pass

    def was_successful(self):
        """Tells whether or not this result was a success."""
        return len(self.failures) == len(self.errors) == 0

    def stop(self):
        """Indicates that the tests should be aborted."""
        self.should_stop = True

    @classmethod
    def strclass(cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    def __repr__(self):
        return "<%s run=%i errors=%i failures=%i>" % \
               (self.strclass(), self.run_count, len(self.errors),
                len(self.failures))

    def begin_test(self):
        pass

    def finish_test(self):
        pass


def _direct_product_test_data(data_source):
    import copy
    arg_stack = [{}]
    for keys, data_list in data_source:
        if not isinstance(keys, (tuple, list)):
            keys = (keys,)
            data_list = [(data,) for data in data_list]
        work_stack = []
        for test_data in data_list:
            #print keys, test_data
            for argument in arg_stack:
                argument = copy.copy(argument)
                if len(keys) != len(test_data):
                    msg = language.get("framework", "data_porvider_error",
                            key=str(keys),data=str(test_data))
                    raise ValueError(msg)
                for i, key in enumerate(keys):
                    argument[key] = test_data[i]
                work_stack.append(argument)
        arg_stack = work_stack[:]
    return arg_stack
