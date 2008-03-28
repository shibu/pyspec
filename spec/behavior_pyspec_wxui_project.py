# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
import StringIO
import pyspec.wxui.project


sample_project_file = """
[Config]
auto_run = True
auto_reload = False
fail_activate = False
success_activate = False
cui_encoding = utf8
function_hook = trace

[Specs]
test_pyspec = D:\\home\\shibu\\pyspec\\pyspec.py
"""


# filename=last_use_time
sample_config = """
fileA.pyspec=2000
fileB.pyspec=1000
fileC.pyspec=3000
"""


class Behavior_WxPySpecProject_read(object):
    @context
    def A_WxProject_object(self):
        file_obj = StringIO.StringIO(sample_project_file)
        self.project = pyspec.wxui.project.WxPySpecProject()
        self.project.read(file_obj)

    @spec
    def should_read_test_options(self):
        About(self.project.auto_run).should_be_true()
        About(self.project.auto_reload).should_be_false()
        About(self.project.fail_activate).should_be_false()
        About(self.project.success_activate).should_be_false()

    @spec
    def should_read_common_options(self):
        About(self.project.cui_encoding).should_be_true()
        About(self.project.function_hook).should_equal("trace")

    @spec
    def should_read_spec_file_list(self):
        About(self.project.specs["test_pyspec"]).should_equal(
                                      "D:\\home\\shibu\\pyspec\\pyspec.py")

class WxPySpecProject_write_Behavior(object):
    @context
    def A_file_written_by_project(self):
        project = pyspec.wxui.project.WxPySpecProject()
        project.auto_run = True
        project.auto_reload = False
        project.auto_activate = False
        project.specs["test_pyspec"] = "D:\\home\\shibu\\pyspec\\pyspec.py"
        file_obj = StringIO.StringIO()
        project.save(file_obj)
        self.dummy_file = StringIO.StringIO(file_obj.getvalue())
        print file_obj.getvalue()

    @spec
    def should_contain_test_options(self):
        project = pyspec.wxui.project.WxPySpecProject()
        project.read(self.dummy_file)
        About(project.auto_run).should_be_true()
        About(project.auto_reload).should_be_false()
        About(project.fail_activate).should_be_false()
        About(project.success_activate).should_be_false()

    @spec
    def should_contain_spec_file_list(self):
        project = pyspec.wxui.project.WxPySpecProject()
        project.read(self.dummy_file)
        About(project.specs["test_pyspec"]).should_equal(
                                       "D:\\home\\shibu\\pyspec\\pyspec.py")


class Behavior_WxPySpecProjectManager(object):
    @context
    def A_ProjectManager(self):
        sample_data = StringIO.StringIO(sample_config)
        self.manager = pyspec.wxui.project.WxPySpecProjectManager(sample_data)
        self.manager.current_time_for_test = 4000

    @spec
    def should_select_recent_file(self):
        recent_file_name = self.manager.get_filepath()
        About(recent_file_name).should_equal("fileC.pyspec")

    @spec
    def can_open_project_file(self):
        recent_file_name = "fileD.pyspec"
        self.manager.open(recent_file_name)
        recent_file_name = self.manager.get_filepath()
        About(recent_file_name).should_equal("fileD.pyspec")

    @spec
    def should_support_save_as(self):
        self.manager.save_as("fileD.pyspec")
        recent_file_name = self.manager.get_filepath()
        last_used_time = self.manager.last_used_time()
        About(recent_file_name).should_equal("fileD.pyspec")
        About(last_used_time).should_equal(4000)

    @spec
    def can_save_an_exist_file(self):
        About(self.manager.can_save()).should_be_true()

    @spec
    def should_save_if_dirty_flag_was_set(self):
        self.manager.set_dirty_flag()
        About(self.manager.should_save()).should_be_true()

    @spec
    def should_not_save_if_dirty_flag_was_not_set(self):
        About(self.manager.should_save()).should_be_false()

    @spec
    def should_not_save_after_save_command(self):
        self.manager.set_dirty_flag()
        self.manager.save()
        About(self.manager.should_save()).should_be_false()

    @spec
    def should_not_save_after_save_as_command(self):
        self.manager.set_dirty_flag()
        self.manager.save_as("fileD.pyspec")
        About(self.manager.should_save()).should_be_false()

    @spec
    def should_have_display_filename(self):
        About(self.manager.display_filename()).should_equal("fileC.pyspec")

    @spec
    def should_have_modified_display_filename_if_file_was_changed(self):
        self.manager.set_dirty_flag()
        About(self.manager.display_filename()).should_equal("* fileC.pyspec *")


class Behavior_WxPySpecProjectManager_ReadProject(object):
    @context
    def A_ProjectManager(self):
        sample_data = StringIO.StringIO(sample_config)
        project_file = StringIO.StringIO(sample_project_file)
        self.manager = pyspec.wxui.project.WxPySpecProjectManager(sample_data)
        self.manager.current_time_for_test = 4000
        self.manager.open(project_file)

    @spec
    def should_return_recent_project_options(self):
        About(self.manager.is_auto_run()).should_be_true()
        About(self.manager.is_auto_reload()).should_be_false()
        About(self.manager.is_fail_activate()).should_be_false()
        About(self.manager.is_success_activate()).should_be_false()


class Behavior_WxPySpecProjectManager_NewFile(object):
    @context
    def A_new_ProjectManager(self):
        sample_data = StringIO.StringIO("")
        self.manager = pyspec.wxui.project.WxPySpecProjectManager(sample_data)
        self.manager.current_time_for_test = 4000

    @spec
    def should_have_a_project_that_is_default_file(self):
        About(self.manager.is_default_file()).should_be_true()

    @spec
    def should_have_default_file_name_project(self):
        About(self.manager.get_filepath()).should_equal("new.pyspec")

    @spec
    def should_have_display_filename(self):
        About(self.manager.display_filename()).should_equal("*new")

    @spec
    def cannot_save_a_default_file(self):
        About(self.manager.can_save()).should_be_false()


if __name__ == "__main__":
    run_test()
