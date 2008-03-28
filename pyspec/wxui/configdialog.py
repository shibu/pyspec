# -*- coding: ascii -*-

__pyspec = 1

import wx
from wx import xrc

__all__ = ("WxConfigDialog",)

class WxConfigDialog(object):
    hook_method_name = ["profile", "trace", "no"]
    def __init__(self, res, parent):
        self.parent = parent
        self.project = None
        self.is_ok = True
        self.dialog = res.LoadDialog(parent, "PYSPEC_CONFIG_DIALOG")
        self.dialog.Bind(wx.EVT_BUTTON, self.cancel, id=xrc.XRCID("CONFIG_CANCEL"))
        self.dialog.Bind(wx.EVT_BUTTON, self.ok, id=xrc.XRCID("CONFIG_OK"))
        self.dialog.Bind(wx.EVT_CLOSE, self.ok)

        self.function_hook = xrc.XRCCTRL(parent, "CONFIG_FUNCTION_HOOK")
        self.check_auto_reload = xrc.XRCCTRL(parent, "CONFIG_AUTO_RELOAD")
        self.check_auto_run = xrc.XRCCTRL(self.dialog, "CONFIG_AUTO_RUN")
        self.check_fail_activate = xrc.XRCCTRL(self.dialog, "CONFIG_FAIL_ACTIVATE")
        self.check_success_activate = xrc.XRCCTRL(self.dialog, "CONFIG_SUCCESS_ACTIVATE")

    def set_option(self, runner):
        self.project = runner.project
        self.update_option()

    def update_option(self):
        index = self.hook_method_name.index(self.project.get_function_hook())
        self.function_hook.SetSelection(index)
        self.check_auto_run.SetValue(self.project.is_auto_run())
        self.check_auto_reload.SetValue(self.project.is_auto_reload())
        self.check_fail_activate.SetValue(self.project.is_fail_activate())
        self.check_success_activate.SetValue(self.project.is_success_activate())

    def show(self):
        self.dialog.ShowModal()
        return self.is_ok

    def ok(self, event):
        self.dialog.EndModal(0)
        self.project.function_hook = self.function_hook.GetSelection()
        self.project.auto_run = self.check_auto_run.IsChecked()
        self.project.auto_reload = self.check_auto_reload.IsChecked()
        self.project.fail_activate = self.check_fail_activate.IsChecked()
        self.project.success_activate = self.check_success_activate.IsChecked()

    def cancel(self, event):
        self.dialog.EndModal(0)
