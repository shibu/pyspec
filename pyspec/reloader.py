# -*- coding: ascii -*-

__pyspec = 1
__all__ = ("ModuleObserver", "ModuleReloader")

import linecache, os, sys, time

class ModuleReloader(object):
    def __init__(self):
        self.modules = {}
        self.observer_class = ModuleObserver
        self.category = MethodCategorizer()

    def check_modification(self):
        changed_modules = []
        for observer in self.modules.itervalues():
            if observer.is_modified():
                changed_modules.append(observer)
        return changed_modules

    def check_new_modules(self):
        new_modules = []
        old_modules = sys.modules.keys()
        try:
            for name, module in sys.modules.iteritems():
                if not self.modules.has_key(name):
                    observer = self.observer_class(module)
                    self.modules[name] = observer
                    new_modules.append(observer)
            old_modules = None
            return new_modules
        finally:
            if old_modules is not None:
                print "new: %s" % set(sys.modules.keys()).difference(set(old_modules))
                print "del: %s" % set(old_modules).difference(sys.modules.keys())

    def update_depends(self, observers):
        for observer in observers:
            if observer.module is not None:
                use_module = observer.make_depends(category=self.category)
                use_module.discard(observer.module.__name__)
                for module_name in use_module:
                    self.modules[module_name].affect.add(observer.module.__name__)

    def clear_flag(self):
        for module in self.modules.itervalues():
            module.change_flag = False

    def clear_callstack(self):
        pass

    def clear_callstack_hostspot(self, method):
        pass

    def dump_structure_map(self):
        print self.category.methods
        table = {}
        for module in self.modules.itervalues():
            module.dump_module_structure_map(table, self.category)
        return table

class ModuleVisitor(object):
    def explore(self, observers, nest=1):
        pass

    def visit_module(self, nest):
        pass

class ModuleObserver(object):
    __slots__ = ("module", "path", "mtime", "affect", "has_error", "change_flag", "is_system", "is_pyspec", "is_spectest")
    def __init__(self, module):
        self.module = module
        self.path = None
        self.mtime = None
        self.affect = set()
        self.has_error = False
        self.module_type_check()
        if not self.is_system:
            self.path = self.check_filename()
            self.mtime = os.path.getmtime(self.path)

    def make_depends(self, namespace = None, result = None, category = None):
        from types import ModuleType, FunctionType, TypeType, ClassType, MethodType
        if namespace is None:
            namespace = self.module
            result = set()
        for name, object in namespace.__dict__.iteritems():
            if name == "__builtins__":
                continue
            elif type(object) == ModuleType:
                if (not self.is_system) and (object is not namespace):
                    result.add(object.__name__)
            elif type(object) == MethodType:
                if category is not None:
                    category.regist_method(object)
            elif type(object) == FunctionType:
                if category is not None:
                    category.regist_method(object)
                if object.__module__ is None:
                    continue
                module = sys.modules[object.__module__]
                if self.is_system:
                    pass
                elif object.__module__ != namespace.__name__:
                    result.add(object.__module__)
            elif type(object) in [TypeType, ClassType]:
                if object.__module__ is None:
                    continue
                try:
                    module = sys.modules[object.__module__]
                    if self.is_system or (module is namespace):
                        pass
                    else:
                        result.add(object.__module__)
                    self.make_depends(object, result, category)
                except KeyError:
                    print "not find '%s'" % object.__module__
        return result

    def module_type_check(self):
        if not hasattr(self.module, "__file__"):
            self.is_system = True
        elif self.module.__file__ == "__main__":
            self.is_system = True
        elif self.module.__file__.startswith(sys.prefix):
            self.is_system = True
        else:
            self.is_system = False

        if hasattr(self.module, "__pyspec"):
            self.is_pyspec = True
        else:
            self.is_pyspec = False

        self.is_spectest = False

    def is_modified(self):
        if self.mtime is None:
            return False
        oldmtime = self.mtime
        self.mtime = os.path.getmtime(self.path)
        return oldmtime != self.mtime

    def reload(self):
        import traceback
        self.has_error = False
        if self.is_system or self.is_pyspec:
            return
        if self.module is not None:
            keys = self.module.__dict__.keys()
            for key in keys:
                if key.startswith("__") and key.endswith("__"):
                    continue
                del self.module.__dict__[key]
        try:
            reload(self.module)
            print "reload(%s)" % self.module.__name__
            if self.mtime is not None:
                self.mtime = os.path.getmtime(self.path)
        except Exception, error:
            print "load error(%s)" % self.module.__name__
            self.has_error = True
            error_message = ''.join(traceback.format_exception(error.__class__, error, None))
            return error_message

    def reload_all(self, modules, error_messages):
        error_message = self.reload()
        self.change_flag = True
        if self.has_error:
            self.chain_error_messages(self.affect, modules, 0, error_messages, error_message)
            return
        self.chain_reload(self.affect, modules, 0)
        update_modules = set()
        for module in modules.itervalues():
            if module.change_flag:
                linecache.checkcache(self.path)

    def chain_reload(self, change_modules, allmodules, i):
        if i > 10:
            return
        next_updates = set()
        for module_name in change_modules:
            observer = allmodules[module_name]
            observer.reload()
            if not observer.has_error:
                next_updates.update(observer.affect)
        if next_updates:
            self.chain_reload(next_updates, allmodules, i+1)

    def chain_error_messages(self, change_modules, allmodules, i, error_messages, error_message):
        if i > 10:
            return
        next_modules = set()
        for module_name in change_modules:
            observer = allmodules[module_name]
            if observer.is_spectest:
                try:
                    error_messages[observer].append(error_message)
                except KeyError:
                    error_messages[observer] = [error_message]
            next_modules.update(observer.affect)
        if next_modules:
            self.chain_error_modules(next_modules, allmodules, i+1, error_messages, error_message)

    def check_filename(self):
        path = self.module.__file__
        if path.endswith(".pyc"):
            return path[:-1]
        elif path.endswith(".pyo"):
            return path[:-1]
        return path

    def dump_module_structure_map(self, table, category_list, namespace = None, nest=False):
        from types import ModuleType, FunctionType, TypeType, ClassType, MethodType
        if not self.is_spectest:
            return
        if namespace is None:
            namespace = self.module
        for name, object in namespace.__dict__.iteritems():
            if name == "__builtins__":
                continue
            elif type(object) in [MethodType, FunctionType]:
                if hasattr(object, "__pyspec_attribute"):
                    self.collect_structure_from_method(table, category_list, object)
            elif (type(object) in [TypeType, ClassType]) and (not nest):
                self.dump_module_structure_map(table, category_list, object, nest=True)

    def collect_structure_from_method(self, table, category_list, function):
        attr = getattr(function, "__pyspec_attribute")
        print attr
        if not hasattr(attr, "call"):
            return
        if attr.call is None:
            return
        stack = [None, None]
        print attr.call.stack
        for frame in attr.call.stack:
            if frame[0] in (0, 3):
                category = category_list.find_category(frame[1])
                if category is not None:
                    stack.append(category)
                else:
                    stack.append(stack[-1])
                if stack[-1] != stack[-2]:
                    try:
                        count = table[(stack[-2], stack[-1])]
                        table[(stack[-2], stack[-1])] = count + 1
                    except KeyError:
                        table[(stack[-2], stack[-1])] = 1
            else:
                stack.pop()

class MethodCategorizer(object):
    def __init__(self):
        self.methods = {}

    def search_docstring(self, docstring):
        if docstring is None:
            return None
        for line in docstring.split("\n"):
            if line.startswith("@category"):
                category = line[len("@category"):].strip()
                return category.split(" ")[0]
        return None

    def check_method(self, method):
        import inspect
        docstring = inspect.getdoc(method)
        return self.search_docstring(docstring)

    def regist_method(self, method):
        category = self.check_method(method)
        if category is None:
            return
        if hasattr(method, "func_code"):
            self.methods[id(method.func_code)] = category
        elif hasattr(method, "im_func"):
            self.methods[id(method.im_func.func_code)] = category

    def find_category(self, func_code_id):
        try:
            return self.methods[func_code_id]
        except KeyError:
            return None
