# -*- coding: ascii -*-

import os
import sys
import types
import inspect
import wx
from wx import xrc
import wx.html
import pyspec.wxui.api as api
from pyspec.util import *
from pyspec.wxui.util import *


class ClassBrowser(object):
    def __init__(self, addin_manager):
        panel = addin_manager.frame
        addin_dir = addin_manager.addin_dir

        imagelist = wx.ImageList(12, 12)
        filepath = os.path.join(addin_dir, 'folder.png')
        imagelist.Add(wx.Image(filepath, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        filepath = os.path.join(addin_dir, 'module.png')
        imagelist.Add(wx.Image(filepath, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        filepath = os.path.join(addin_dir, 'class.png')
        imagelist.Add(wx.Image(filepath, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        filepath = os.path.join(addin_dir, 'method.png')
        imagelist.Add(wx.Image(filepath, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        filepath = os.path.join(addin_dir, 'text.png')
        imagelist.Add(wx.Image(filepath, wx.BITMAP_TYPE_PNG).ConvertToBitmap())

        self.module_tree = xrc.XRCCTRL(panel, "MODULE_TREE")
        self.module_tree.AssignImageList(imagelist)
        self.module_tree.AddRoot("root")
        self.class_tree = xrc.XRCCTRL(panel, "CLASS_TREE")
        self.class_tree.SetImageList(imagelist)
        self.search_word = xrc.XRCCTRL(panel, "SEARCH_WORD")
        self.search_result = xrc.XRCCTRL(panel, "SEARCH_RESULT")
        self.html_view = xrc.XRCCTRL(panel, "HTML_VIEW")
        self.html_view.OnLinkClicked = self.link_clicked

        self.node_list = {}
        self.index_list = {}

        addin_manager.add_listener("class_browser", BrowserModuleNode,
                                   BrowserClassNode, BrowserMethodNode, self)
        bind_event_handler(panel, self)

    def link_clicked(self, link):
        print link

    def add_module(self, module_name, module):
        if module_name in self.node_list:
            self.node_list[module_name].module = module
            return

        names = module_name.split(".")
        parent = self.module_tree.GetRootItem()
        for i in xrange(len(names)):
            node_name = ".".join(names[0:i+1])
            if not self.node_list.has_key(node_name):
                count = self.module_tree.GetChildrenCount(parent, False)
                if count == 0:
                    new_node = self.module_tree.AppendItem(parent, names[i], 1)
                else:
                    new_node = self._insert_module(names[i], parent, count)
                if i != 0:
                    self.module_tree.Expand(parent)
                self.node_list[node_name] = Struct(tree_node=new_node,
                                                   module=None)
                parent = new_node
            else:
                parent = self.node_list[node_name].tree_node
        self.node_list[module_name].module = module

    def _insert_module(self, last_name, parent, count):
        compare_name = last_name.lower()
        children = []
        child, cookie = self.module_tree.GetFirstChild(parent)
        children.append(child)
        for i in xrange(count-1):
            child, cookie = self.module_tree.GetNextChild(parent, cookie)
            children.append(child)
        for i, child in enumerate(children):
            target = self.module_tree.GetItemText(child).lower()
            if last_name < target:
                return self.module_tree.InsertItemBefore(parent, i, last_name, 1)
        node = self.module_tree.AppendItem(parent, last_name, 1)
        return node

    @expose(wx.EVT_TREE_SEL_CHANGED, id="MODULE_TREE")
    def generate_tree(self, event):
        module = None
        for node in self.node_list.itervalues():
            if node.tree_node == event.GetItem():
                module = node.module
                break
        if module is None:
            print "generate_tree: module is None"
            return
        self.class_tree.DeleteAllItems()
        root = self.class_tree.AddRoot("root")
        module.add_node(self.class_tree, root)
        self.html_view.SetPage(module.create_html())

    @expose(wx.EVT_TREE_SEL_CHANGED, id="CLASS_TREE")
    def anchor_select(self, event):
        print "anchor_select"


class BrowserModuleNode(api.ModuleAspect):
    def __init__(self, observer):
        super(BrowserModuleNode, self).__init__(observer)
        self.browser = None
        self.index_node = None

    def get_filename(self):
        name = self.module().target().__name__
        if name == "__main__" or name == "":
            filename = os.path.basename(self.module().target().__file__)
            return os.path.splitext(filename)[0]
        return name

    def init(self, browser):
        self.browser = browser
        browser.add_module(self.name(), self)

    def add_node(self, treectrl, root):
        self.index_node = treectrl.AppendItem(root, "index", 4)
        for classobj in self.classes():
            classobj.add_node(treectrl, root)
        for method in self.methods():
            method.add_node(treectrl, root)

    def create_html(self):
        index = 1
        head = [["font", {"size":6}, "Module: %s" % self.get_filename()], ["hr"]]
        brief = ["table", {"border":1,
                           "cellpadding":3,
                           "cellspacing":0,
                           "width":"100%"},
                    ["tr", {"bgcolor":"#CCCCFF"},
                        ["td", {"colspan":2}, ["font", {"size":4}, ["b", "Index"]]]]]
        for classobj in self.classes(sort=True):
            index = classobj.create_brief(brief, index)
        for method in self.methods(sort=True):
            index = method.create_brief(brief, index)
        description = []
        for classobj in self.classes():
            index = classobj.create_description(description, index)
        for method in self.methods():
            method.create_description(description)
        html  = head + [brief] + description
        return format_html(html)


class BrowserClassNode(api.ClassAspect):
    def __init__(self, observer):
        super(BrowserClassNode, self).__init__(observer)
        self.browser_node = None
        self.index = None

    def add_node(self, treectrl, root):
        if self.defined_here():
            self.browser_node = treectrl.AppendItem(root, self.name(), 2)
            for method in self.methods():
                method.add_node(treectrl, self.browser_node)

    def create_brief(self, html, index):
        pyspec_aspect = self.find_aspect("pyspec")
        if not self.defined_here():
            return index
        else:
            if isinstance(self.target(), object):
                classtype = "class"
            else:
                classtype = "old style class"

            html.append(["tr",
                            ["td",
                                ["font", {"size":3, "color":"blue"}, classtype],
                                ["a", {"href":"#%d" % (index+1)},
                                      ["tt", self.name()]]],
                            ["td", pyspec_aspect.short_description()]])
            self.index = index + 1
            return index + 1

    def create_description(self, html, index):
        if not self.defined_here():
            return index
        html.append(["hr"])
        if isinstance(self.target(), object):
            html.append(["h4", "class %s" % self.name()])
        else:
            html.append(["h4", "old style class %s" % self.name()])
        method_table = ["table", {"border":1,
                           "cellpadding":3,
                           "cellspacing":0,
                           "width":"100%"}]
        for method in self.methods(sort=True):
            method.create_brief(method_table, None)
        html.append(method_table)
        return index


class BrowserMethodNode(api.MethodAspect):
    def __init__(self, observer):
        super(BrowserMethodNode, self).__init__(observer)
        self.browser_node = None
        self.browser = None
        self.index = None

    def add_node(self, treectrl, parent):
        if self.defined_here():
            self.browser_node = treectrl.AppendItem(parent, self.name(), 3)

    def create_brief(self, html, index):
        pyspec_aspect = self.find_aspect("pyspec")
        if not self.defined_here():
            return index
        else:
            if index is not None:
                name = ["method", ["a", {"href":"#%d" % (index+1)},
                                  ["tt", self.name()]]]
                self.index = index + 1
                return self.index
            else:
                name = ["method", ["tt", self.name()]]
            html.append(["tr",
                            ["td"] + name,
                            ["td", pyspec_aspect.short_description()]])

    def create_description(self, html):
        if not self.defined_here():
            return
        pyspec_aspect = self.find_aspect("pyspec")
        methodtype = ""
        if type(self.target()) is types.MethodType:
            methodtype = "method"
        else:
            methodtype = "function"
        args = inspect.getargspec(self.target())
        argspec = inspect.formatargspec(*args)
        html.append(["hr"])
        html.append(["a", {"name": str(self.index)},
                        ["font", {"size":3, "color":"blue"}, methodtype],
                        ["font", {"size":3},
                            ["b", "%s%s" % (self.name(), argspec)]]])
        description = pyspec_aspect.description()
        if description is not None:
            html.append(["p", pyspec_aspect.description()])


@api.entry_point
def init_classbrowser_plagin(addin_manager):
    resource_path = os.path.join(addin_manager.addin_dir, "classbrowser.xrc")
    resource = xrc.XmlResource(resource_path)
    addin_manager.add_main_tab(resource, "CLASSBROWSER", "Class Browser")
    browser = ClassBrowser(addin_manager)
    return browser
