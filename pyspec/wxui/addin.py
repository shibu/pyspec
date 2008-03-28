# -*- coding: ascii -*-

__pyspec = 1

import os
import sys
import imp

import wx
from wx import xrc

import pyspec.api
import pyspec.util
import pyspec.wxui.util
from graphvizdialog import WxGraphVizDialog


class AddinLoader(object):
    addin_list = {}
    addin_name = ""
    addin_menu_id = 101

    @classmethod
    def add_entry_point(cls, method):
        cls.addin_list[cls.addin_name].entry_points.append(method)

    @classmethod
    def add_event_handler(cls, method, event_type):
        cls.addin_list[cls.addin_name].event_handler[event_type] = method

    @classmethod
    def add_addin_menu(cls, method, menu_title):
        id = cls.addin_menu_id
        cls.addin_list[cls.addin_name].addin_menu[id] = (method,
                                                         menu_title)
        cls.addin_menu_id += 1

    def guess_addin_dir(self):
        wxui_addin_dir = pyspec.util.pyspec_file_path("wxaddin")
        if os.path.exists(wxui_addin_dir):
            return wxui_addin_dir
        raise ValueError("addin_dir %s not found" % wxui_addin_dir)

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
                root, ext = os.path.splitext(filename)
                if ext in [".py", ".pyc", ".pyo"]:
                    addin_list[root] = addin_dir

        method_list = []
        pyspec.api.loader = self
        for module_name, dirname in addin_list.iteritems():
            AddinLoader.addin_name = module_name
            addin = pyspec.util.Struct(entry_points=[], event_handler={},
                                       addin_menu={}, addin=None,
                                       dirname=dirname)
            AddinLoader.addin_list[module_name] = addin
            f, fn, desc = imp.find_module(module_name, [addin_dir])
            imp.load_module(module_name, f, fn, desc)


class AddinManager(object):
    def __init__(self, resource, frame, kernel):
        self.resource = resource
        self.frame = frame
        self.kernel = kernel
        self.addin_dir = None
        self.main_tab = xrc.XRCCTRL(self.frame, "PYSPEC_MAIN_TAB")
        self.inspect_tab = xrc.XRCCTRL(self.frame, "PYSPEC_INSPECT_TAB")
        menubar = self.frame.GetMenuBar()
        self.addin_menu = menubar.GetMenu(menubar.FindMenu("Addin"))
        self.graphviz_dialog = WxGraphVizDialog(self.resource, self.frame)
        self.graphviz_dialog.bind_event_handler()

    def load_addin(self):
        loader = AddinLoader()
        loader.load_addin()
        for filename, addin in AddinLoader.addin_list.iteritems():
            #print filename, addin
            self.addin_dir = addin.dirname
            for entry_point in addin.entry_points:
                addin.addin = entry_point(self)
            for menu_id, menu in addin.addin_menu.iteritems():
                function, title = menu
                self.addin_menu.Append(menu_id, title, title)
                self.frame.Bind(wx.EVT_MENU, self.menu_handle, id=menu_id)

    def menu_handle(self, event):
        menu_id = event.GetId()
        for addin in AddinLoader.addin_list.itervalues():
            if menu_id in addin.addin_menu:
                function, title = addin.addin_menu[menu_id]
                function(addin.addin)

    def add_menu_in_addin_menubar(self, name, function):
        menuid = "WXADDIN_" + name.replace("&", "")
        self.menu_handler_list[self.menu_id] = (function, argv)
        self.addin_menu.Append(self.menu_id, name, description)
        self.frame.Bind(wx.EVT_MENU, self.menu_handle, id=self.menu_id)
        self.menu_id += 1

    def add_main_tab(self, resource, xrckey, name):
        panel = resource.LoadPanel(self.main_tab, xrckey)
        self.main_tab.AddPage(panel, name)

    def get_new_main_tab(self, name):
        panel = wx.Panel(self.main_tab)
        self.main_tab.AddPage(panel, name)
        return panel

    def add_inspect_tab(self, resource, xrckey, name):
        panel = resource.LoadPanel(self.inspect_tab, xrckey)
        self.inspect_tab.AddPage(panel, name)

    def get_new_inspect_tab(self, name):
        panel = wx.Panel(self.inspect_tab)
        self.inspect_tab.AddPage(panel, name)
        return panel

    def add_listener(self, aspect, ModuleType, ClassType=None, MethodType=None, *init_arg):
        self.kernel.modules.add_listener(aspect, ModuleType, ClassType, MethodType, *init_arg)

    def get_module_observer(self):
        return self.kernel.modules


def call_event_handler(event_type, *args):
    for addin in AddinLoader.addin_list.itervalues():
        for key, handler in addin.event_handler.iteritems():
            if event_type in addin.event_handler:
                addin.event_handler[event_type](addin.addin, *args)
