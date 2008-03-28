# -*- coding: ascii -*-

__pyspec = 1

import os
import types
import inspect

import wx
from wx import xrc
import pyspec.util
import pyspec.wxui.framework

from pyspec.wxui.util import *
from pyspec.wxui.const import *


class WxFormInitializer(object):
    def __init__(self, app, res):
        self.frame = app.frame

        imagelist = wx.ImageList(12, 12)
        imagelist.Add(load_png(get_resource_path('notrun.png')))
        imagelist.Add(load_png(get_resource_path('ignored.png')))
        imagelist.Add(load_png(get_resource_path('success.png')))
        imagelist.Add(load_png(get_resource_path('failure.png')))
        imagelist.Add(load_png(get_resource_path('error.png')))
        imagelist.Add(load_png(get_resource_path('loadfail.png')))

        self.spec_explorer = xrc.XRCCTRL(self.frame, "SPEC_EXPLORER")
        self.spec_explorer.AddRoot("root")
        self.spec_explorer.AssignImageList(imagelist)

        base = xrc.XRCCTRL(self.frame, "PROGRESS_BAR_POSITION")
        self.progressbar = WxPySpecProgressBar(base, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.progressbar, 1, wx.EXPAND)
        base.SetSizer(sizer)

        self.spec_result_list = xrc.XRCCTRL(self.frame, "SPEC_RESULT_LIST")
        self.spec_result_list.InsertColumn(0, "", width=16)
        self.spec_result_list.InsertColumn(1, "File(Line)", width=250)
        self.spec_result_list.InsertColumn(2, "Spec", width=450)
        self.spec_result_list.SetImageList(imagelist, wx.IMAGE_LIST_SMALL)

        self.statusbar = xrc.XRCCTRL(self.frame, "STATUSBAR")
        self.spec_name = xrc.XRCCTRL(self.frame, "SPEC_NAME")
        self.spec_method_info = xrc.XRCCTRL(self.frame, "SPEC_METHOD_INFO")
        self.spec_file_info = xrc.XRCCTRL(self.frame, "SPEC_FILE_INFO")
        self.test_result = xrc.XRCCTRL(self.frame, "VERIFY_RESULT")
        self.consoleout = xrc.XRCCTRL(self.frame, "CONSOLE_OUT")
        self.verify_button = xrc.XRCCTRL(self.frame, "VERIFY_BUTTON")
        self.callstack_button = xrc.XRCCTRL(self.frame, "CALL_STACK_BUTTON")
        self.set_callstack_button(enable=False)

    def set_verify_button_label(self, label):
        self.verify_button.SetLabel(label)

    def clear_all(self):
        self.clear_tree_icon()
        self.spec_result_list.DeleteAllItems()
        self.progressbar.reset()
        self.clear_method_info()

    def clear_spec_explorer(self):
        root = self.spec_explorer.GetRootItem()
        self.spec_explorer.DeleteChildren(root)


    def clear_method_info(self):
        self.test_result.Clear()
        self.consoleout.Clear()
        self.spec_method_info.SetValue("")
        self.spec_name.SetValue("")
        self.spec_file_info.SetValue("")
        self.selected_method = None

    def clear_tree_icon(self, node = None):
        if node is None:
            node = self.spec_explorer.GetRootItem()
        if self.spec_explorer.GetItemImage(node) != 5:
            self.spec_explorer.SetItemImage(node, 0)
        child, cookie = self.spec_explorer.GetFirstChild(node)
        while child.IsOk():
            self.clear_tree_icon(child)
            child, cookie = self.spec_explorer.GetNextChild(child, cookie)

    def set_callstack_button(self, enable=True):
        self.callstack_button.Enable(enable)


class WxPySpecProgressBar(wx.Panel):
    NORMAL = 1
    IGNORED = 2
    FAILURE = 3

    def __init__(self, parent, ID):
        super(WxPySpecProgressBar, self).__init__(parent, ID)
        self.range = 100
        self.value = 0
        self.color_code = WxPySpecProgressBar.NORMAL
        self.color_db = [[(224, 224, 224), (192, 192, 192), (160, 160, 160)],
                         [(228, 255, 216), (210, 255, 191),
                          (165, 255, 127), (121, 255, 63),
                          (76, 255, 0), (68, 216, 0)],
                         [(255, 248, 216), (255, 244, 191),
                          (255, 233, 127), (255, 223, 63),
                          (255, 211, 0), (216, 180, 0)],
                         [(255, 216, 216), (255, 191, 191),
                          (255, 127, 127), (255, 63, 63),
                          (255, 0, 0), (216, 0, 0)]]
        # (s,v) = (15, 100), (25, 100), (50, 100),
        #         (75, 100), (100, 100), (100, 85)
        bind_event_handler(self)

    @expose(wx.EVT_PAINT)
    def on_paint(self, event):
        width, height = self.GetClientSizeTuple()
        positions = [(0.7, 1.0), (0.1, 0.75), (0.0, 0.15)]
        dc = wx.PaintDC(self)
        self._draw_bars(dc, positions, self.color_db[0], width)
        if self.value != 0:
            positions = [(0.0, 0.4), (0.3, 0.6), (0.5, 0.7),
                        (0.7, 0.9), (0.8, 1.0), (0.9, 1.0)]
            actual_width = int(float(width) * self.value / self.range)
            for i, position in enumerate(positions):
                colors = self.color_db[self.color_code]
                self._draw_bars(dc, positions, colors, actual_width)
        self._draw_frame(dc)

    def _draw_bars(self, dc, positions, colors, draw_width):
        width, height = self.GetClientSizeTuple()
        for i, position in enumerate(positions):
            color = wx.Colour(colors[i][0], colors[i][1], colors[i][2])
            dc.SetPen(wx.Pen(color, 1))
            dc.SetBrush(wx.Brush(color))
            dc.DrawRoundedRectangle(0, height*position[0],
                                    draw_width, height*position[1], 2)

    def _draw_frame(self, dc):
        width, height = self.GetClientSizeTuple()
        colors = self.color_db[0]
        color = wx.Colour(colors[-1][0], colors[-1][1], colors[-1][2])
        dc.SetBrush(wx.Brush(color, wx.TRANSPARENT))
        dc.SetPen(wx.Pen(color, 1))
        dc.DrawRoundedRectangle(0, 0, width, height, 2)

    def set_max(self, max_number):
        self.reset(max_number)
        self.range = max_number

    def increment(self, code):
        self.value += 1
        self.color_code = max(self.color_code, code)
        self.Refresh()

    def reset(self, max_number=100):
        self.range = max_number
        self.value = 0
        self.color_code = 1
        self.Refresh()


class WxResultPresenter(object):
    def __init__(self, app, res, initializer):
        self.frame = app.frame
        self.spec_explorer = xrc.XRCCTRL(app.frame, "SPEC_EXPLORER")
        self.statusbar = xrc.XRCCTRL(app.frame, "STATUSBAR")
        self.progressbar = initializer.progressbar
        self.spec_result_list = xrc.XRCCTRL(self.frame, "SPEC_RESULT_LIST")

        self.spec_name = xrc.XRCCTRL(app.frame, "SPEC_NAME")
        self.spec_method_info = xrc.XRCCTRL(app.frame, "SPEC_METHOD_INFO")
        self.spec_file_info = xrc.XRCCTRL(app.frame, "SPEC_FILE_INFO")
        self.test_result = xrc.XRCCTRL(self.frame, "VERIFY_RESULT")
        self.consoleout = xrc.XRCCTRL(self.frame, "CONSOLE_OUT")

        self.attrs = []
        attr = self.consoleout.GetDefaultStyle()
        self.attrs.append(wx.TextAttr(attr.GetTextColour(),
                                      attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.RED, attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.BLUE, attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.Colour(0, 0, 128),
                                      attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.Colour(0, 183, 100),
                                      attr.GetBackgroundColour()))
        self.view_mode = VIEW_RT_ALL

    def _get_fileinfo(self, test):
        filename = inspect.getsourcefile(test.method())
        linenum = inspect.getsourcelines(test.method())
        try: # Fixme
            return "%s(%d)"% (os.path.basename(filename), linenum[1])
        except TypeError:
            return str(test.method)


    def init_progressbar_range(self, range):
        self.progressbar.set_max(range)

    def print_method_test_result(self, item):
        self.print_test_result(item)
        self.print_console(item)
        self.selected_method = item
        spec_method = item.find_aspect("pyspec")
        self.spec_name.SetValue(spec_method.spec_name())
        self.spec_method_info.SetValue(str(spec_method))
        self.spec_file_info.SetValue(self._get_fileinfo(spec_method))

    def print_class_test_result(self, item):
        self.spec_name.SetValue("")
        self.spec_method_info.SetValue("")
        self.spec_file_info.SetValue("")

    def print_module_test_result(self, item):
        self.print_test_result(item)
        self.spec_name.SetValue("")
        self.spec_method_info.SetValue("")
        self.spec_file_info.SetValue("")

    def print_test_result(self, target):
        self.test_result.SetValue("")
        if target is not None:
            spec = target.find_aspect("pyspec")
            if hasattr(spec, "console"):
                for line in spec.console:
                    if line[0] == pyspec.util.CONTEXT_INFO:
                        self.test_result.SetDefaultStyle(self.attrs[2])
                        self.test_result.AppendText("%s\n" % line[1])
                        self.test_result.SetDefaultStyle(self.attrs[0])
                    if line[0] == pyspec.util.REPORT_OUT:
                        self.test_result.AppendText("%s ... " % line[1][1])
                        self.test_result.SetDefaultStyle(self.attrs[3])
                        self.test_result.AppendText("OK\n")
                        self.test_result.SetDefaultStyle(self.attrs[0])
            lines = spec.test_result.split("\n")
            for line in lines:
                if "Error: " in line:
                    token = line.split("Error: ")
                    self.test_result.SetDefaultStyle(self.attrs[1])
                    self.test_result.AppendText("%sError: " % token[0])
                    self.test_result.SetDefaultStyle(self.attrs[0])
                    self.test_result.AppendText("%s\n" % token[1])
                elif line == "OK":
                    self.test_result.SetDefaultStyle(self.attrs[3])
                    self.test_result.AppendText("OK\n")
                    self.test_result.SetDefaultStyle(self.attrs[0])
                else:
                    self.test_result.AppendText("%s\n" % line)


    def print_console(self, method):
        self.consoleout.Clear()
        for line in method.find_aspect("pyspec").console:
            self.consoleout.SetDefaultStyle(self.attrs[line[0]])
            if line[0] != pyspec.util.REPORT_OUT:
                self.consoleout.AppendText(line[1])
            else:
                self.consoleout.AppendText("%s\n" % (line[1][1]))

    def print_status(self, str):
        self.statusbar.SetStatusText(str, 0)

    def print_testcase_count(self, runner):
        text = "All Specs: %d" % runner.get_all_test_count()
        self.statusbar.SetStatusText(text, 1)

    def print_time(self, takentime):
        timestring = ""
        if takentime < 1.0:
            timestring = "%.03fms" % (takentime * 1000)
        else:
            timestring = "%.03fs" % takentime
        self.statusbar.SetStatusText("Time: %s" % timestring, 5)

    def print_testresult_count(self, result):
        self.statusbar.SetStatusText("Specs Run: %d" % result.run_count, 2)
        self.statusbar.SetStatusText("Failures: %d" % len(result.failures), 3)
        self.statusbar.SetStatusText("Errors: %d" % len(result.errors), 4)

    def print_title(self, runner):
        title = "PySpec wxSpecVerifier - %s" % runner.project.display_filename()
        self.frame.SetTitle(title)

    def set_parent_icon(self, node):
        parent = self.spec_explorer.GetItemParent(node)
        parent_icon = self.spec_explorer.GetItemImage(parent)
        child_icon = self.spec_explorer.GetItemImage(node)
        self.spec_explorer.SetItemImage(parent, max(parent_icon, child_icon))
        if parent != self.spec_explorer.GetRootItem():
            self.set_parent_icon(parent)

    def print_success(self, result, test):
        spec = test.find_aspect("spec_tree_node")
        self.progressbar.increment(WxPySpecProgressBar.NORMAL)

        if RT_SUCCESS in self.view_mode:
            self.spec_explorer.SetItemImage(spec.treenode, RT_SUCCESS)
            self.set_parent_icon(spec.treenode)
        else:
            self.spec_explorer.Delete(spec.treenode)
            spec.treenode = None
        wx.SafeYield()

    def print_error_and_failure(self, result, test, err):
        spec = test.find_aspect("spec_tree_node")
        self.progressbar.increment(WxPySpecProgressBar.FAILURE)

        if spec.result_type in self.view_mode:
            exctype, value, tb = err
            self.print_result_to_list(test)
            self.spec_explorer.SetItemImage(spec.treenode, spec.result_type)
            self.set_parent_icon(spec.treenode)
        else:
            self.spec_explorer.Delete(spec.treenode)
            spec.treenode = None
        wx.SafeYield()

    def print_ignore(self, result, test):
        spec = test.find_aspect("spec_tree_node")
        self.progressbar.increment(WxPySpecProgressBar.IGNORED)

        if RT_IGNORED in self.view_mode:
            self.print_result_to_list(test)
            self.spec_explorer.SetItemImage(spec.treenode, RT_IGNORED)
            self.set_parent_icon(spec.treenode)
        else:
            self.spec_explorer.Delete(spec.treenode)
            spec.treenode = None
        wx.SafeYield()

    def print_result_to_list(self, test):
        spec = test.find_aspect("spec_tree_node")
        i = self.spec_result_list.GetItemCount()
        self.spec_result_list.InsertImageItem(i, spec.result_type)
        self.spec_result_list.SetStringItem(i, 1, self._get_fileinfo(test))
        self.spec_result_list.SetStringItem(i, 2, test.short_name()+"()")
