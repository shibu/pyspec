# -*- coding: ascii -*-

__pyspec = 1

import StringIO
import wx
import wx.html
from wx import xrc
import pyspec.wxui.graphvizdialog
from pyspec.util import Struct
from pyspec.wxui.util import *


class StackViewer(object):
    def __init__(self, res, parent):
        self.res = res
        self.dialog = res.LoadDialog(parent, "PYSPEC_CALL_STACK_DIALOG")
        self.viewer = xrc.XRCCTRL(self.dialog, "GRAPH_VIEWER")
        self.call_tree = xrc.XRCCTRL(self.dialog, "CALL_TREE")
        self.stack_info = xrc.XRCCTRL(self.dialog, "STACK_INFO")
        self.module_list = xrc.XRCCTRL(self.dialog, "MODULE_LIST")
        self.method = None
        self.module_browser = None
        self.treenodes = {}
        self.module_filter = set()
        bind_event_handler(self.dialog, self)
        self.attrs = []
        attr = self.stack_info.GetDefaultStyle()
        self.attrs.append(wx.TextAttr(attr.GetTextColour(),
                                      attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.BLUE, attr.GetBackgroundColour()))
        self.attrs.append(wx.TextAttr(wx.RED, attr.GetBackgroundColour()))
        self.graphviz = pyspec.wxui.graphvizdialog.Graphviz()

    def show(self, method, module_browser):
        self.method = method
        self.module_browser = module_browser

        self._set_module_list()
        self._print_callstack()
        self.recreate_call_graph()

        self.dialog.CentreOnScreen()
        self.dialog.ShowModal()

    def _set_module_list(self):
        module_names = []
        system_dict = dict(self.module_browser.system_modules)
        system_module_names = self._output_module_name_filter(system_dict)
        for module_name in system_module_names:
            if module_name.startswith("_"):
                continue
            module_names.append(module_name)
        user_dict = {}
        for module in self.module_browser.get_modules("pyspec"):
            user_dict[module.name()] = module.target()
        user_module_names = self._output_module_name_filter(system_dict, user_dict)
        for module_name in user_module_names:
            module_names.append(module_name)
            self.module_filter.add(module_name)

        self.module_list.InsertItems(module_names, 0)
        for i in xrange(len(system_module_names), self.module_list.GetCount()):
            self.module_list.Check(i, True)

    @staticmethod
    def _output_module_name_filter(system_modules, target_modules=None):
        if target_modules is None:
            target_modules = system_modules
        for name in target_modules.keys():
            if name.startswith("_") or name.startswith("encodings."):
                del target_modules[name]
            elif "." in name:
                last_name = name.split(".")[-1]
                if last_name in system_modules or last_name.startswith("_"):
                    del target_modules[name]
        key_list = target_modules.keys()
        key_list.sort()
        return key_list

    def _print_callstack(self):
        self.treenodes = {}
        self.call_tree.DeleteAllItems()
        root = self.call_tree.AddRoot("stack trace")

        stack = self._create_call_stack(self.method.stack)
        if len(stack) > 0:
            for childstack in stack:
                self._add_stack(childstack, root)
        self.call_tree.ExpandAll()

    def _create_call_stack(self, callinfo):
        print self.module_filter
        calltree = []
        stack = [calltree]
        for frame in callinfo[:-1]:
            if frame.event_code in (0, 3):
                last = stack[-1]
                last.append([frame])
                stack.append(last[-1])
            else:
                stack.pop()
        return stack[0]

    def _add_stack(self, stack, treenode):
        print stack[0].module_name, "in self.module_filter = ", stack[0].module_name in self.module_filter
        if "About.__init__" in stack[0].name():
            return
        elif stack[0].module_name in self.module_filter:
            print "  add node"
            newnode = self.call_tree.AppendItem(treenode, stack[0].name())
            self.treenodes[newnode] = stack[0]
        else:
            newnode = treenode
        if len(stack) > 1:
            for childstack in stack[1:]:
                self._add_stack(childstack, newnode)

    @expose(wx.EVT_CLOSE)
    @expose(wx.EVT_BUTTON, id="CLOSE_BUTTON")
    def close(self, event):
        self.dialog.EndModal(0)

    @expose(wx.EVT_TREE_SEL_CHANGED, id="CALL_TREE")
    def show_frame_information(self, event):
        self.stack_info.SetValue("")
        selected_node = event.GetItem()
        for treenode, stack in self.treenodes.iteritems():
            if treenode == selected_node:
               break
        self._out_stack("Name:", 1)
        self._out_stack("  %s" % stack.name())
        if stack.instance_id != None:
           self._out_stack("Instance:", 1)
           self._out_stack("  %s" % stack.get_instance_name())
           self._out_stack("    (id=0x%x)" % stack.instance_id)
        self._out_stack("Module Name:", 1)
        self._out_stack("  defined at %s" % stack.module_name)

    def _out_stack(self, text, attr=0):
        self.stack_info.SetDefaultStyle(self.attrs[attr])
        self.stack_info.AppendText("%s\n" % text)

    @expose(wx.EVT_CHECKLISTBOX, id="MODULE_LIST")
    def init_module_filter(self, event):
        self.module_filter = set()
        for i in xrange(self.module_list.GetCount()):
            if self.module_list.IsChecked(i):
                self.module_filter.add(self.module_list.GetString(i))

    @expose(wx.EVT_BUTTON, id="REFRESH_BUTTON")
    def recreate_call_graph(self, event=None):
        source = dump_communication_diagram(self.method)
        self.graphviz.add_source("communication", source)
        self.graphviz.select_last()
        self.graphviz.generate()
        self.viewer.SetPage(self.graphviz.get_html())


def dump_communication_diagram(method, is_simple=True):
    objects, messages = collect_communication(method.stack)

    out = StringIO.StringIO()
    print >>out, "digraph G {"
    print >>out, '  node [style="filled", shape="box", fontname="Helvetica", fontsize=11, color="limegreen", fillcolor="palegreen"];'
    print >>out, '  edge [fontname="Helvetica", fontsize=11, color="darkgreen"];'
    print >>out, '  graph [dpi=72];'

    for id, node in objects.iteritems():
        print >>out, '  %d [label="%s"];' % (id, node)

    for connect, messagelist in messages.iteritems():
        message_strings = []
        for message in messagelist:
            if is_simple:
                output_name = "%s" % message.name
                if output_name not in message_strings:
                    message_strings.append(output_name)
            else:
                if message.count != 1:
                    message_strings.append("%d: %s *%d" % (message.id, message.name, message.count))
                elif ".__init__()" in message.name:
                    message_strings.append("%d: <<new>>" % (message.id))
                else:
                    message_strings.append("%d: %s" % (message.id, message.name))
        print >>out, '  %d -> %d [label="%s"];' % (connect[0], connect[1], "\\n".join(message_strings))

    print >>out, "}"
    return out.getvalue()

def collect_communication(callstack):
    messages = {}
    objects = {}
    stack = []
    message_id = 1
    for frame in callstack:
        if frame.event_code in (0, 3):
            id = frame.instance_id
            stack.append(id)
            if id is None:
                continue
            if len(stack) > 1 and (stack[-1] != stack[-2]) and (None not in stack[-2:]):
                try:
                    message = messages[(stack[-2], stack[-1])]
                    if message[-1].name == frame.name() and (message[-1].id+1) == message_id:
                        message[-1].count = message[-1].count + 1
                    else:
                        message.append(Struct(name=frame.name(), id=message_id, count=1))
                        message_id = message_id + 1
                except KeyError:
                    messages[(stack[-2], stack[-1])] = [Struct(name=frame.name(), id=message_id, count=1)]
                    message_id = message_id + 1
            try:
                if objects[id] == "self":
                    objects[id] = frame.get_instance_name()
            except KeyError:
                objects[id] = frame.get_instance_name()
        else:
            if stack:
                stack.pop()
            #else:
            #    print "stack is empty"
    return objects, messages
