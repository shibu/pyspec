# -*- coding: ascii -*-

__pyspec = 1

import os
import sys
import imp

import pyspec.api
import pyspec.util


class AddinLoaderBase(object):
    def __init__(self, addin_folder_name=""):
        self.addin_folder_name = addin_folder_name

    addin_list = {}
    addin_name = ""
    addin_menu_id = 101

    @classmethod
    def add_entry_point(cls, method):
        cls.addin_list[cls.addin_name].entry_points.append(method)

    @classmethod
    def add_event_handler(cls, method, event_type):
        cls.addin_list[cls.addin_name].event_handler[event_type] = method

    def guess_addin_dir(self):
        addin_dir = pyspec.util.pyspec_file_path(self.addin_folder_name)
        if os.path.exists(addin_dir):
            return addin_dir
        raise ValueError("addin_dir %s not found" % addin_dir)

    def load_addin(self):
        addin_list = {}
        addin_dir = self.guess_addin_dir()
        sys.path.append(addin_dir)
        for filename in os.listdir(addin_dir):
            filepath = os.path.join(addin_dir, filename)
            if os.path.isdir(filepath):
                dirname = filepath
                filepath = os.path.join(filepath, "__init__.py")
                if os.path.exists(filepath):
                    addin_list[filename] = dirname
            else:
                root, ext = os.path.splitext(filepath)
                if ext in [".py", ".pyc", ".pyo"]:
                    addin_list[root] = root
        pyspec.api.loader = self
        for module_name, dirname in addin_list.iteritems():
            AddinLoaderBase.addin_name = module_name
            addin = pyspec.util.Struct(entry_points=[], event_handler={},
                                       addin_menu={}, addin=None,
                                       dirname=dirname)
            AddinLoaderBase.addin_list[module_name] = addin
            f, fn, desc = imp.find_module(module_name, [addin_dir])
            imp.load_module(module_name, f, fn, desc)


class AddinManagerBase(object):
    def __init__(self, kernel):
        self.kernel = kernel

    def load_addin(self, loader):
        loader.load_addin()
        for filename, addin in AddinLoaderBase.addin_list.iteritems():
            #print filename, addin
            self.addin_dir = addin.dirname
            for entry_point in addin.entry_points:
                addin.addin = entry_point(self)
        self.call_event_handler = call_event_handler

    def add_listener(self, aspect, ModuleType, ClassType=None, MethodType=None, *init_arg):
        self.kernel.modules.add_listener(aspect, ModuleType, ClassType, MethodType, *init_arg)

    def get_module_observer(self):
        return self.kernel.modules


def call_event_handler(event_type, *args):
    for addin in AddinLoaderBase.addin_list.itervalues():
        handler = addin.event_handler.get(event_type)
        if handler is not None:
            handler(addin.addin, *args)
