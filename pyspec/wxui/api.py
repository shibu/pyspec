# -*- coding: ascii -*-

"""PySpec extension api.
   This module enable following extension features:
     - Add aspect to modules, classes, methods
     - Add Add-in
"""


__pyspec = 1


import os
import sys


class AspectBase(object):
    """Base class of ModuleAspect, ClassAspect, MethodAspect."""
    __slots__ = ('observer',)
    def __init__(self, observer):
        self.observer = observer

    def target(self):
        return self.observer.target

    def name(self):
        return self.observer.get_name()

    def find_listener(self, ModuleType):
        return self.observer.find_listener(ModuleType)

    def find_aspect(self, aspect):
        return self.observer.find_aspect(aspect)


class ModuleAspect(AspectBase):
    """Additional module information class(base class).
    Derive this and regist, you can add any information about tha module.
    And, you can use Visitor Pattern easily.
    """
    def __init__(self, observer):
        super(ModuleAspect, self).__init__(observer)

    module = AspectBase.target

    def methods(self, sort=False, sort_by=None):
        return self.observer.get_methods(self, sort, sort_by)

    functions = methods

    def classes(self, sort=False, sort_by=None):
        return self.observer.get_classes(self, sort, sort_by)

    def children(self):
        return self.functions() + self.classes()

    def is_system(self):
        return self.observer.is_system

    def module(self):
        return self


class ClassAspect(AspectBase):
    def __init__(self, observer):
        super(ClassAspect, self).__init__(observer)

    classobj = AspectBase.target

    def methods(self, sort=False, sort_by=None):
        return self.observer.get_methods(self, sort, sort_by)

    children = methods

    def module(self):
        """return module that this method is defined."""
        index = self.observer.index(type(self))
        return self.observer.module[index][1]

    def defined_here(self):
        """return True if this class was defined in this module."""
        try:
            return sys.modules[self.target().__module__] is self.module().target()
        except KeyError:
            return False


class MethodAspect(AspectBase):
    """base class for adding method aspect.
    """
    def __init__(self, observer):
        super(MethodAspect, self).__init__(observer)

    method = AspectBase.target

    def parent(self):
        """return parent(class or module)."""
        index = self.observer.index(type(self))
        return self.observer.parent[index][1]

    def module(self):
        """return module that this method is defined."""
        if self.observer.module is None:
            return None
        index = self.observer.index(type(self))
        return self.observer.module[index][1]

    def defined_here(self):
        """return True if this method/function was defined in this module."""
        try:
            return sys.modules[self.target().__module__] is self.module().target()
        except KeyError:
            return False


def entry_point(method):
    """Notify the target method is special function of pyspec extension.
    Method name must be in folloing list:
      add_tab() : Add new tab in main dialog
      add_inspect_tab() : Add new tab in inspection area
      add_module_observer() : Regist module observer
      add_command() :
      add_trace() :
      add_profile() :

    """
    if "pyspec.wxui.addin" in sys.modules:
        addin = sys.modules["pyspec.wxui.addin"]
        addin.AddinLoader.add_entry_point(method)


class EventHandlerRegister(object):
    def __init__(self, event_type):
        self.event_type = event_type

    def __call__(self, method):
        if "pyspec.wxui.addin" in sys.modules:
            addin = sys.modules["pyspec.wxui.addin"]
            addin.AddinLoader.add_event_handler(method, self.event_type)
        return method


class MenuRegister(object):
    def __init__(self, menu_label):
        self.menu_label = menu_label

    def __call__(self, method):
        if "pyspec.wxui.addin" in sys.modules:
            addin = sys.modules["pyspec.wxui.addin"]
            addin.AddinLoader.add_addin_menu(method, self.menu_label)
        return method


def event_handler(event_type):
    if event_type not in ("on_spec_select", "on_module_select", "on_class_select"):
        ValueError("Invalid event type: %s" % event_type)
    return EventHandlerRegister(event_type)


def addin_menu_item(name):
    return MenuRegister(name)
