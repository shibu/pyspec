# -*- coding: ascii -*-

__pyspec = 1

"""These classes serve aspect support for modules, classes, methodes.

If you use this module, you can add some information to modules, classes,
and methods. In pyspec, methods can have test result themselves and several
methods for judgement of method type and suppor of running test.

@sa api.py
"""

import os
import re
import imp
import sys
import types
import inspect
import linecache

import pyspec.api
from pyspec.util import split_path


def _default_sort_function(x, y):
    return cmp(x.name().lower(), y.name().lower())


class Notifier(object):
    def __init__(self, name, target):
        self.target = target
        self.listener_list = []
        self.name = str(name)

    def add_listener(self, aspect, listener):
        self.listener_list.append((aspect, listener))

    def notify(self, index_or_aspect, method, args):
        listener = self.find_aspect(index_or_aspect)
        try:
            method = getattr(listener, method)
        except AttributeError:
            return
        return method(*args)

    def find_aspect(self, index_or_aspect):
        if type(index_or_aspect) is int:
            return self.listener_list[index_or_aspect][1]
        elif type(index_or_aspect) is str:
            is_find = False
            for aspect, listener in self.listener_list:
                if aspect == index_or_aspect:
                    return listener
            if not is_find:
                raise KeyError("aspect '%s' is not registered" % index_or_aspect)
        else:
            msg = "first parameter must be int or str, %s passed" \
                                                 % str(type(index_or_aspect))
            raise TypeError(msg)

    def index(self, aspect_or_observer):
        if type(aspect_or_observer) is str:
            aspect = aspect_or_observer
            for i, listener in enumerate(self.listener_list):
                if listener[0] is aspect:
                    return i
            raise KeyError("listener aspect '%s' is not registered" % aspect)
        observer = aspect_or_observer
        for i, listener in enumerate(self.listener_list):
            if type(listener[1]) is observer:
                return i
        raise KeyError("listener type '%s' is not registered" % str(observer))

    def __getitem__(self, index):
        return self.listener_list[index]

    def get_name(self):
        return self.name

    def find_listener(self, ListenerType):
        for listener in self.listener_list:
            if type(listener) is ListenerType:
                return listener
        raise KeyError("cannot find listenr of %s" % str(ListenerType))


class ModuleObserver(Notifier):
    def __init__(self, name, target_module, browser):
        "call super"
        super(ModuleObserver, self).__init__(name, target_module)
        self.classes = {}
        self.functions = {}
        self.path = None
        self.mtime = None
        self.has_error = False
        self.module_type_check()
        self.browser = browser
        if not self.is_system:
            self.path = self.check_filename()
            self.mtime = os.path.getmtime(self.path)
            if target_module is None:
                self.has_error = True
            else:
                self.init_content()

    def add_listener(self, listener_type):
        """add new listner."""
        aspect = listener_type[0]
        ModuleType = listener_type[1]
        super(ModuleObserver, self).add_listener(aspect, ModuleType(self))
        for classobj in self.classes.itervalues():
            classobj.add_listener(listener_type)
        for function in self.functions.itervalues():
            function.add_listener(listener_type)

    def init_content(self):
        self.classes = {}
        self.functions = {}

        for name in dir(self.target):
            obj = getattr(self.target, name)
            if type(obj) in (types.TypeType, types.ClassType):
                self.classes[name] = ClassObserver(name, obj, self)
            elif type(obj) is types.FunctionType:
                self.functions[name] = MethodObserver(name, obj, self, self)

    def check_filename(self):
        path = self.target.__file__
        if path.endswith(".pyc"):
            return path[:-1]
        elif path.endswith(".pyo"):
            return path[:-1]
        return path

    def module_type_check(self):
        """check this module is sysmtem module or not."""
        if not hasattr(self.target, "__file__"):
            self.is_system = True
        elif self.target.__file__ in ["__main__", None]:
            self.is_system = True
        elif self.target.__file__.startswith(sys.prefix):
            self.is_system = True
        else:
            self.is_system = False

    def is_modified(self):
        if self.mtime is None:
            return False
        oldmtime = self.mtime
        self.mtime = os.path.getmtime(self.path)
        return oldmtime != self.mtime

    def remove(self, new_module):
        self.target = new_module
        for class_observer in self.classes:
            class_observer.remove()
        for method_observer in self.methods:
            method_observer.remove()

        self.search_module()

        self.notify("reload")

    def get_methods(self, listner, sort=False, sort_by=None):
        if sort_by is None and sort is True:
            sort_by = _default_sort_function
        index = self.index(type(listner))
        methods = [method[index][1] for method in self.functions.itervalues()]
        if sort_by is not None:
            methods.sort(sort_by)
        return methods

    get_functions = get_methods

    def get_classes(self, listner, sort=False, sort_by=None):
        if sort_by is None and sort is True:
            sort_by = _default_sort_function
        index = self.index(type(listner))
        classes = [classobj[index][1] for classobj in self.classes.itervalues()]
        if sort_by is not None:
            classes.sort(sort_by)
        return classes


class ClassObserver(Notifier):
    def __init__(self, name, target_class, module):
        super(ClassObserver, self).__init__(name, target_class)
        self.module = module
        self.methods = {}
        self.test_class = False
        if module is None:
            self.test_class = True
        #elif inspect.getmodule(target_class) is not module.target:
        elif target_class.__module__ != module.target.__name__:
            self.is_valid = False
            return
        self.is_valid = True
        for name in dir(target_class):
            obj = getattr(target_class, name)
            if type(obj) in [types.MethodType, types.FunctionType]:
                self.methods[name] = MethodObserver(name, obj, module, self)

    def remove(self):
        self.notify("remove")
        self.notify_list = []

    def add_listener(self, listener_type):
        aspect = listener_type[0]
        ClassType = listener_type[2]
        super(ClassObserver, self).add_listener(aspect, ClassType(self))
        for method in self.methods.itervalues():
            method.add_listener(listener_type)

    def get_methods(self, listner, sort=False, sort_by=None):
        if sort_by is None and sort is True:
            sort_by = _default_sort_function
        index = self.index(type(listner))
        methods = [method[index][1] for method in self.methods.itervalues()]
        if sort_by is not None:
            methods.sort(sort_by)
        return methods


class MethodObserver(Notifier):
    def __init__(self, name, target_method, module, parent):
        super(MethodObserver, self).__init__(name, target_method)
        self.module = module
        self.parent = parent

    def remove(self):
        self.notify("remove")
        self.notify_list = []

    def add_listener(self, listener_type):
        aspect = listener_type[0]
        MethodType = listener_type[3]
        super(MethodObserver, self).add_listener(aspect, MethodType(self))


class ModuleBrowser(object):
    """ModuleBrowser check all loaded modules, notify message.
    This module is used by test runner, class browser and module reloader etc.
    """
    def __init__(self):
        self.listener_types = []
        self.user_modules = []
        self.system_modules = {}
        self.unused_modules = set()
        self.package_names = []

    @staticmethod
    def _import(filepath):
        """This code from Python Cookbook:
           http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/159571
        """
        (path, name) = os.path.split(filepath)
        (name, ext) = os.path.splitext(name)

        (file, filename, data) = imp.find_module(name, [path])
        return imp.load_module(name, file, filepath, data)

    def load_module(self, filepath):
        filepath = os.path.abspath(filepath)
        dirname = os.path.dirname(filepath)
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        if dirname not in sys.path:
            sys.path.insert(0, dirname)
        module = self._import(filepath)
        return self.load_single(module, module_name)

    @staticmethod
    def _get_module_name(filepath):
        return os.path.splitext(os.path.basename(filepath))[0]

    def remove_module(self, module):
        remove_list = []
        for i, user_module in enumerate(self.user_modules):
            if user_module is module.observer:
                remove_list.append(i)
        remove_list.reverse()
        for i in remove_list:
            del self.user_modules[i]

    def load_single(self, module, name):
        new_module_observer = self._new_module_observer(module, name)
        self._clear_system_module_list()
        if new_module_observer is None:
            return
        return self._load_user_module(new_module_observer)

    def load_all(self):
        """Load all modules in sys.modules.
        """
        new_modules = []
        module_names = sys.modules.keys()
        module_names.sort()
        for module_name in module_names:
            module = sys.modules[module_name]
            new_module_observer = self._new_module_observer(module, module_name)
            if new_module_observer is not None:
                new_modules.append(new_module_observer)
        self._clear_system_module_list()
        for new_module in new_modules:
            self._load_user_module(new_module)

    def _load_user_module(self, new_module_observer):
        """the method for adding new module.
        """
        if not self._module_name_filter(new_module_observer.get_name()):
            self.unused_modules.add(new_module_observer.target)
            return
        file_path = new_module_observer.target.__file__
        if "__init__.py" in file_path:
            match = re.match(r"(.+)__init__\.py", file_path)
            self.package_names.append(match.groups()[0])
            self.package_names.sort()
        else:
            self._renew_module_name(new_module_observer)
        self.user_modules.append(new_module_observer)
        for index, listener_type in enumerate(self.listener_types):
            new_module_observer.add_listener(listener_type)
        for index, listener_type in enumerate(self.listener_types):
            new_module_observer.notify(index, "init", listener_type[-1])
        return new_module_observer

    def _renew_module_name(self, observer):
        file_path = observer.target.__file__
        for package_path in self.package_names:
            if file_path.startswith(package_path):
                relative_path = file_path[len(package_path):]
                relative_path = relative_path[0:relative_path.find(".py")]
                names = split_path(relative_path)
                names.insert(0, split_path(package_path)[-1])
                observer.name = ".".join(names)
                break

    def _module_name_filter(self, module_name):
        if module_name.startswith("_"):
            if module_name == "__main__":
                return True
            return False
        elif module_name.startswith("encodings."):
            return False
        elif "." in module_name:
            last_name = module_name.split(".")[-1]
            if last_name in self.system_modules:
                return False
            elif last_name.startswith("_"):
                return False
        return True

    def _clear_system_module_list(self):
        module_names = []
        remove_list = []
        for module_name in self.system_modules.iterkeys():
            if module_name.startswith("_"):
                remove_list.append(module_name)
            elif not self._module_name_filter(module_name):
                remove_list.append(module_name)
        for name in remove_list:
            self.unused_modules.add(self.system_modules.pop(name))

    def _new_module_observer(self, module, module_name):
        if module_name in self.system_modules:
            return None
        if module in self.unused_modules:
            return None
        module_observer = ModuleObserver(module_name, module, self)
        if module_observer.is_system:
            self.system_modules[module_name] = module
            return None
        return module_observer

    def add_listener(self, aspect, ModuleType,
                                   ClassType=pyspec.api.ClassAspect,
                                   MethodType=pyspec.api.MethodAspect, *init_args):
        listener_type = (aspect, ModuleType, ClassType, MethodType, init_args)
        self.listener_types.append(listener_type)

        for module in self.user_modules:
            module.add_listener(listener_type)

        for module in self.user_modules:
            module.notify(-1, "init", init_args)

    def send_all(self, aspect, message, *args):
        """Send a message to all module observers.
        """
        for i in xrange(len(self.listener_types)):
            listener_type = self.listener_types[i]
            if listener_type[0] is aspect:
                for module in self.user_modules:
                    module.notify(i, message, args)
                break

    def get_modules(self, aspect):
        index = None
        for i, listener_type in enumerate(self.listener_types):
            if listener_type[0] == aspect:
                index = i
                break
        if index is None:
            return []
        result = []
        for module in self.user_modules:
            result.append(module[index][1])
        return result

