# -*- coding: ascii -*-

__pyspec = 1

import wx
import wx.html
from wx import xrc

import pyspec.util
from pyspec.wxui.util import *

__all__ = ("WxGraphVizDialog",)

class WxGraphVizDialog(object):
    def __init__(self, res, parent):
        self.parent = parent
        self.dialog = res.LoadDialog(parent, "PYSPEC_GRAPHVIZ_DIALOG")
        self.viewer = xrc.XRCCTRL(self.dialog, "GRAPH_VIEWER")
        self.category = xrc.XRCCTRL(self.dialog, "GRAPH_CATEGORY")
        self.graphviz = Graphviz()
        self.remove_files = []

    def bind_event_handler(self):
        bind_event_handler(self.dialog, self)

    def set_title(self, title):
        self.graphviz.clear()
        self.dialog.SetTitle(title)

    def set_source(self, name, source):
        self.graphviz.add_source(name, source)

    @expose(wx.EVT_COMBOBOX, id="GRAPH_CATEGORY")
    def reload(self, event):
        selected = self.category.GetStringSelection()
        self.graphviz.generate()
        self.graphviz.select(selected)
        self.viewer.SetPage(self.graphviz.get_html())

    def show(self):
        self.category.Clear()
        for category in self.graphviz.category():
            self.category.Append(category)
        self.category.SetSelection(0)
        self.reload(None)
        #print self.graphviz.image_filepath()
        image = wx.Image(self.graphviz.image_filepath(), wx.BITMAP_TYPE_PNG)
        sizer = self.dialog.GetSizer()
        sizer.SetItemMinSize(self.viewer, min(image.GetWidth()+20, 800), min(image.GetHeight()+40, 700))
        self.dialog.SetSize(sizer.GetMinSize())
        self.dialog.CentreOnScreen()
        self.dialog.ShowModal()

    @expose(wx.EVT_CLOSE)
    @expose(wx.EVT_BUTTON, id="GRAPH_CLOSE_BUTTON")
    def close(self, event):
        self.graphviz.remove()
        self.dialog.EndModal(0)

    @expose(wx.EVT_BUTTON, id="GRAPH_SAVE_BUTTON")
    def save(self, event):
        import shutil
        dialog = wx.FileDialog(self.dialog, message="Structure Map Output",
                wildcard = "*.png")
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self.graphviz.save(dialog.GetPath())
        dialog.Destroy()


class Graphviz(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.sources = []
        self.selected = 0

    def add_source(self, name, source):
        source = pyspec.util.Struct(name=name, source=source, path="")
        self.sources.append(source)

    def category(self):
        result = []
        for source in self.sources:
            result.append(source.name)
        return result

    def select(self, name):
        category = self.category()
        self.selected = category.index(name)

    def select_last(self):
        self.selected = len(self.sources) - 1

    def source(self):
        return self.sources[self.selected]

    def image_filepath(self):
        return self.source().path + ".png"

    def get_html(self):
        return pyspec.util.format_html([["img", {"src":self.image_filepath()}]])

    def save(self, destination):
        shutil
        distination = dialog.GetPath()
        if not destination.endswith(".png"):
            destination = destination + ".png"
        shutil.copyfile(self.image_filepath(), destination)

    def remove(self):
        import os
        for source in self.sources:
            try:
                os.remove(source.path)
            except:
                pass
            try:
                os.remove(source.path + ".png")
            except:
                pass

    def generate(self):
        import os, tempfile
        for source in self.sources:
            if source.path != "":
                continue
            temp = tempfile.mkstemp(suffix=".dot")
            source.path = temp[1]
            out = os.fdopen(temp[0], "w")
            print >>out, source.source
            out.close()
            os.system("dot.exe -Tpng %s > %s.png" % (source.path, source.path))

