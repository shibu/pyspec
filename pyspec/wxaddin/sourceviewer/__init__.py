# -*- coding: ascii -*-

import os
import sys
import types
import inspect
import wx
import wxpystyletext
import pyspec.wxui.api as api


@api.event_handler("on_spec_select")
@api.event_handler("on_class_select")
@api.event_handler("on_module_select")
def on_method_select(source_viewer, method):
    target = method.target()
    module = method.find_aspect("pyspec").module()
    try:
        target_source = inspect.getsourcelines(target)
        module_source = inspect.getsource(module.target())
        source_viewer.SetReadOnly(0)
        source_viewer.SetValue(module.decode(module_source))
        if target_source[1] > 0:
            source_viewer.HideLines(1, target_source[1]-2)
        total_lines = source_viewer.GetLineCount()
        next_line_position = target_source[1] + len(target_source[0])
        source_viewer.HideLines(next_line_position, total_lines-1)
        source_viewer.SetReadOnly(1)
    except TypeError:
        pass


@api.entry_point
def init_sourcecodeviewer_plagin(addin_manager):
    base = addin_manager.get_new_inspect_tab("SourceCode")
    viewer = wxpystyletext.PythonStyleTextControl(base, -1)
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(viewer, 1, wx.EXPAND)
    base.SetSizer(sizer)
    return viewer
