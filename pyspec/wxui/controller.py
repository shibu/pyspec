# -*- coding: ascii -*-

__pyspec = 1

import os
import time
import wx
import wx.html
from wx import xrc

import pyspec.util
import pyspec.wxui.addin as addin
import pyspec.wxui.framework as framework
import pyspec.wxui.presenter as presenter
import pyspec.wxui.stackviewer as stackviewer
import pyspec.wxui.configdialog as configdialog

from pyspec.wxui.util import *
from pyspec.wxui.const import *

#import simple_test

__all__ = ("WxPySpecController",)

class WxPySpecController(wx.App):
    def OnInit(self):
        """init GUI application class.
        """
        self.res = xrc.XmlResource(get_resource_path("wxpyspec.xrc"))
        self._init_event()
        self.initializer = presenter.WxFormInitializer(self, self.res)
        self.result_presenter = presenter.WxResultPresenter(self, self.res,
                                                            self.initializer)
        self.tester = framework.WxSpecTester()
        self._init_option()
        self.tester.check_loaded_modules()
        self.addin = addin.AddinManager(self.res, self.frame,
                                        self.tester.kernel)
        self.addin.load_addin()
        self.timer.Start(2000)
        return True

    def _init_event(self):
        """init event handlers.
        @category init.event
        """
        self.frame = self.res.LoadFrame(None, "PYSPEC_MAIN_FRAME")
        self.SetTopWindow(self.frame)
        self.config_dialog = pyspec.wxui.configdialog.WxConfigDialog(self.res, self.frame)

        menubar = self.frame.GetMenuBar()
        self.filemenu = menubar.GetMenu(menubar.FindMenu("File"))
        self.recent_file_id = xrc.XRCID("MENU_FILE_RECENT_FILES")
        self.recentfile_ids = [xrc.XRCID("MENU_FILE_RECENT_FILES_%d" % i) for i in xrange(1, 6)]
        for id in self.recentfile_ids:
            self.frame.Connect(id, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.file_recent)
        self.spec_explorer = xrc.XRCCTRL(self.frame, "SPEC_EXPLORER")
        self.timer = wx.Timer(self.frame)
        bind_event_handler(self.frame, self)
        self.frame.Show()

    def _init_option(self):
        print ".",
        self.tester.init_check(self.result_presenter)
        print ".",
        self.config_dialog.set_option(self.tester)
        print ".",
        self.result_presenter.print_title(self.tester)
        print ".",
        #self._update_recent_file()
        print ".",

    def clear_result(self):
        self.initializer.clear_all()
        self.result = None

    @expose(wx.EVT_TIMER)
    def auto_reload(self, evnet):
        if self.tester.project.is_auto_reload():
            self.project_reload(None)

    def get_selected_item(self):
        selected_items = self.spec_explorer.GetSelections()
        if len(selected_items) != 1:
            return ("None", None)
        treenode = selected_items[0]
        for spec_module in self.tester.kernel.modules.get_modules("spec_tree_node"):
            if spec_module.treenode == treenode:
                return ("module", spec_module)
            for method in spec_module.methods():
                if method.treenode == treenode:
                    return ("method", method)
            for classobj in spec_module.classes():
                if classobj.treenode == treenode:
                    return ("class", classobj)
                for method in classobj.methods():
                    if method.treenode == treenode:
                        return ("method", method)

    @expose(wx.EVT_TREE_SEL_CHANGED, id="SPEC_EXPLORER")
    def print_spec_on_tree(self, event):
        item_type, item_obj = self.get_selected_item()
        self.initializer.set_callstack_button(enable=False)
        if item_type == "None":
            self.initializer.clear_method_info()
        elif item_type == "module":
            self.result_presenter.print_module_test_result(item_obj)
            addin.call_event_handler("on_module_select", item_obj)
        elif item_type == "class":
            self.result_presenter.print_class_test_result(item_obj)
            addin.call_event_handler("on_class_select", item_obj)
        elif item_type == "method":
            self.result_presenter.print_method_test_result(item_obj)
            addin.call_event_handler("on_spec_select", item_obj)
            self.initializer.set_callstack_button(enable=True)

    @expose(wx.EVT_LIST_ITEM_SELECTED, id="SPEC_RESULT_LIST")
    def print_spec_on_list(self, event):
        index = event.GetIndex()
        if self.result_presenter.view_mode == "ignored":
            method = self.result.ignored_methods[index]
        else:
            method = self.result.failure_methods[index]
        treenode = method.find_aspect("spec_tree_node")
        self.spec_explorer.UnselectAll()
        self.spec_explorer.SelectItem(treenode.treenode)
        self.result_presenter.print_method_test_result(method)
        addin.call_event_handler("on_spec_select", method)
        self.initializer.set_callstack_button(enable=True)

    @expose(wx.EVT_BUTTON, id="VERIFY_BUTTON")
    def verify(self, event):
        selections = self.spec_explorer.GetSelections()
        self.tester.find_tests(selections)
        self._verify_spec()

    @expose(wx.EVT_BUTTON, id="VERIFY_ALL_BUTTON")
    @expose(wx.EVT_MENU, id="MENU_PROJECT_VERIFY_ALL")
    def verify_all(self, event):
        self.tester.select_all()
        self._verify_spec()

    def _verify_spec(self):
        self.clear_result()
        self.initializer.set_verify_button_label("Stop")
        test_count = len(self.tester)
        self.result = framework.WxSpecResultRecorder(self.result_presenter, test_count)
        self.result_presenter.print_testresult_count(self.result)
        self.result_presenter.print_time(0.0)
        starttime = time.time()
        self.tester.run(self.result)
        stoptime = time.time()
        takentime = stoptime - starttime
        self.result_presenter.print_time(takentime)
        self.result_presenter.print_status("Completed %d specs" % len(self.tester))
        self.initializer.set_verify_button_label("Verify")
        if self.result.was_successful():
            if self.tester.project.is_success_activate():
                self.frame.Raise()
        else:
            if self.tester.project.is_fail_activate():
                self.frame.Raise()

    @expose(wx.EVT_MENU, id="MENU_PROJECT_ADD")
    def project_add(self, event):
        dialog = wx.FileDialog(self.frame, message="Test module select",
                wildcard = "*.py")
        result = dialog.ShowModal()
        path = dialog.GetPath()
        dialog.Destroy()
        if result == wx.ID_OK:
            try:
                module = self.tester.append(path)
                self.result_presenter.print_status("\"%s\" module(%d tests) successfully loaded." % (module.name(), len(module)))
                self.result_presenter.print_testcase_count(self.tester)
                self.clear_result()
                self.tester.check_loaded_modules()
                self.result_presenter.print_title(self.tester)
                if self.tester.project.is_auto_run():
                    self.run_all(None)
            except framework.NoTestCaseNotifier:
                filename = os.path.split(dialog.GetPath())[1]
                errormsg = "File \"%s\" has no test classes or methods." \
                                                    % os.path.basename(path)
                message = wx.MessageDialog(self.frame, errormsg, "Error",
                                           wx.OK | wx.ICON_QUESTION)
                message.ShowModal()
                message.Destroy()
            except ImportError:
                self.result_presenter.print_status("\"%s\" has errors" % os.path.basename(path))

    @expose(wx.EVT_MENU, id="MENU_PROJECT_DEL")
    def project_delete(self, event):
        filelist = [spec.name() for spec in self.tester.spec_modules]
        dialog = wx.MultiChoiceDialog(self.frame, "Select modules to delete.", "Delete Modules", filelist)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            select_items = dialog.GetSelections()
            for i in select_items:
                self.tester.delete(filelist[i], self.spec_explorer)
            self.result_presenter.print_status("%d modules was deleted." % len(select_items))
            self.result_presenter.print_testcase_count(self.tester)
            self.result_presenter.print_title(self.tester)
        dialog.Destroy()
        self.clear_result()

    @expose(wx.EVT_MENU, id="MENU_PROJECT_FIND")
    def project_find(self, event):
        dialog = wx.DirDialog(self.frame, message="Add all test modules in selected directory.",
                defaultPath=os.path.abspath("."))
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            if self.tester.search_dir(dialog.GetPath(), self.spec_explorer):
                self.result_presenter.print_status("%d modules successfully loaded." % result)
                self.result_presenter.print_testcase_count(self.tester)
                self.clear_result()
                self.tester.check_modules()
                self.result_presenter.print_title(self.tester)
            else:
                self.result_presenter.print_status("No module was found.")
        dialog.Destroy()
        if self.tester.option.auto_run:
            self.run_all(None)

    @expose(wx.EVT_BUTTON, id="RELOAD_BUTTON")
    @expose(wx.EVT_MENU, id="MENU_PROJECT_RELOAD")
    def project_reload(self, event):
        if self.tester.update() == True:
            self.result_presenter.print_status("Reloaded.")
            self.result_presenter.print_testcase_count(self.tester)
            self.clear_result()
            if self.tester.option.auto_run:
                self.run_all(None)
        else:
            self.result_presenter.print_status("No module was modified.")

    @expose(wx.EVT_MENU, id="MENU_PROJECT_CONFIG")
    def project_config(self, event):
        self.config_dialog.show()

    @expose(wx.EVT_MENU, id="MENU_FILE_NEW")
    def file_new(self, event):
        if not self.confirm_save():
            return
        self.tester.clear_all(self.spec_explorer)
        self.tester.project.add_new_project()
        self.result_presenter.print_title(self.tester)

    @expose(wx.EVT_MENU, id="MENU_FILE_OPEN")
    def file_open(self, event):
        if not self.confirm_save():
            return
        msg = "Open Test Project File(*.pyspec)."
        filedialog = wx.FileDialog(self.frame, message=msg, wildcard="*.pyspec")
        result = filedialog.ShowModal()
        if result == wx.ID_OK:
            self.file_new(None)
            self.tester.open(self.spec_explorer,
                             self.spec_list, filedialog.GetPath())
            self.result_presenter.print_title(self.tester)
            self._update_recent_file()
            self.tester.check_loaded_modules()
        filedialog.Destroy()

    def confirm_save(self):
        if self.tester.project.should_save():
            dialog = wx.MessageDialog(self.frame, 'Project file was modified. Save before exit?',
                'Save before exit?',
                wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION)
            result = dialog.ShowModal()
            dialog.Destroy()
            if result == wx.ID_YES:
                filedialog = wx.FileDialog(self.frame, message="Test module select",
                        wildcard = "*.pyspec")
                result = filedialog.ShowModal()
                if result == wx.ID_OK:
                    self.tester.save(filedialog.GetPath())
                filedialog.Destroy()
                self.result_presenter.print_title(self.tester)
            elif result == wx.ID_CANCEL:
                return False
        return True

    def file_recent(self, event):
        menu_id = self.recentfile_ids.index(event.GetId())
        filepath = self.tester.project.projects[menu_id].get_filepath()
        if not os.path.exists(filepath):
            dialog = wx.MessageDialog(self.frame, 'Following file has been deleted alread.\n%s' % filepath,
                'File Open Error', wx.OK | wx.ICON_ERROR)
            dialog.Destroy()
            return
        self.tester.clear_all(self.spec_explorer)
        self.tester.open(self.spec_explorer, filepath)
        self.result_presenter.print_title(self.tester)
        self._update_recent_file()

    @expose(wx.EVT_MENU, id="MENU_FILE_SAVE")
    def file_save(self, event):
        if self.tester.project.can_save():
            self.tester.save()
            status = "Save setting file: %s" % self.tester.project.get_filepath()
            self.result_presenter.print_status(status)
            self.result_presenter.print_title(self.tester)
        else:
            self.file_saveas()

    @expose(wx.EVT_MENU, id="MENU_FILE_SAVEAS")
    def file_saveas(self, event=None):
        filepath = self.tester.project.get_filepath()
        if filepath is None:
            filepath = self.tester.project.home_file_path("default.pyspec")
        default_file = os.path.basename(filepath)
        default_dir = os.path.dirname(filepath)
        filedialog = wx.FileDialog(self.frame, message="Save Test Project File(*.pyspec).",
                wildcard="*.pyspec", defaultFile=default_file, defaultDir=default_dir)
        result = filedialog.ShowModal()
        if result == wx.ID_OK:
            self.tester.save(filedialog.GetPath())
            status = "Save setting file: %s" % self.tester.project.get_filepath()
            self.result_presenter.print_status(status)
            self.result_presenter.print_title(self.tester)
            self._update_recent_file()
        filedialog.Destroy()

    @expose(wx.EVT_CLOSE)
    @expose(wx.EVT_MENU, id="MENU_FILE_QUIT")
    def file_quit(self, event):
        self.file_new(None)
        wx.Exit()

    def create_structure_map(self, event):
        #self.graphviz_dialog.set_title("Software Construction Map")
        source = self.tester.module_reloader.reloader.dump_structure_map()
        #self.graphviz_dialog.set_source("map", source)
        #self.graphviz_dialog.show()
        print source

    def _update_recent_file(self):
        recentfiles = self.filemenu.FindItemById(self.recent_file_id).GetSubMenu()
        for i, menuitem in enumerate(recentfiles.GetMenuItems()):
            id = menuitem.GetId()
            recentfiles.Delete(id)
            filepath = self.tester.project.get_filepath()
            if filepath is None:
                break
            recentfiles.Append(id, "&%d : %s" % (i+1, filepath))

    @expose(wx.EVT_RADIOBOX, id="EXPLORER_OPTION")
    def set_view_mode(self, event):
        index = event.GetSelection()
        mode = (VIEW_RT_ALL, VIEW_RT_FAILURE, VIEW_RT_IGNORED)
        self.result_presenter.view_mode = mode[index]
        self.initializer.clear_spec_explorer()
        self.tester.recreate_tree(self.result_presenter)

    @expose(wx.EVT_BUTTON, id="CALL_STACK_BUTTON")
    def show_call_stack(self, event):
        type, method = self.get_selected_item()
        if type != "method":
            return
        stack_viewer = stackviewer.StackViewer(self.res, self.frame)
        stack_viewer.show(method.find_aspect("pyspec"),
                          self.tester.kernel.modules)

