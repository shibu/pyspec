# -*- coding: ascii -*-

__pyspec = 1

import os
import time
import ConfigParser
import pyspec.util
import pyspec.project


class WxPySpecProject(pyspec.project.PySpecProject):
    def __init__(self, file_or_filename=None, last_used_time=None):
        super(WxPySpecProject, self).__init__(file_or_filename, does_read=False)
        if last_used_time is None:
            self.last_used_time = time.time()
        else:
            self.last_used_time = last_used_time

    def _clear_all(self):
        super(WxPySpecProject, self)._clear_all()
        self.auto_run = False
        self.auto_reload = False
        self.fail_activate = False
        self.success_activate = False

    def _read_template(self, parser):
        self._read_bool_option(parser, "Config", "auto_run")
        self._read_bool_option(parser, "Config", "auto_reload")
        self._read_bool_option(parser, "Config", "fail_activate")
        self._read_bool_option(parser, "Config", "success_activate")

    def _save_template(self, parser):
        parser.set("Config", "auto_run", str(self.auto_run))
        parser.set("Config", "auto_reload", str(self.auto_reload))
        parser.set("Config", "fail_activate", str(self.fail_activate))
        parser.set("Config", "success_activate", str(self.success_activate))


class WxPySpecProjectManager(object):
    def __init__(self, test_data=None):
        self.projects = []
        self.dirty_flag = False
        if test_data is None:
            filepath = pyspec.util.home_path("pyspec.conf")
            if os.path.exists(filepath):
                self._read_setting_file(file(filepath))
                self._current().read()
            else:
                self.add_new_project()
            self.test_mode = False
        else:
            self._read_setting_file(test_data)
            self.test_mode = True
        self.current_time_for_test = None

    def _read_setting_file(self, fileobj):
        for line in fileobj.readlines():
            if line.strip() == "":
                continue
            filename, last_use = line.split("=")
            self.projects.append(WxPySpecProject(filename, last_use))
        if len(self.projects) == 0:
            self.add_new_project()
        else:
            self.projects.sort(key=lambda o: o.last_used_time)

    def _update_config_files(self):
        if len(self.projects) > 5:
            self.projects.sort(key=lambda o: o.last_used_time)
            self.projects = self.projects[-5:]
        if self.test_mode:
            return
        user_setting = file(pyspec.util.home_path("pyspec.conf"), "w")
        for option in self.projects:
            user_setting.write("%s=%d\n" % (option.get_filepath(),
                                            option.last_used_time))
        user_setting.close()

    def _current(self):
        return self.projects[-1]

    def _current_time(self):
        if not self.test_mode:
            return time.time()
        return self.current_time_for_test

    def add_new_project(self):
        self.projects.append(WxPySpecProject())

    def open(self, filepath_or_file):
        if not isinstance(filepath_or_file, basestring):
            self._current().read(filepath_or_file)
            return
        is_new = True
        for project in self.projects:
            if filepath_or_file == project.get_filepath():
                is_new = False
                project.last_used_time = self._current_time()
        if is_new:
            self.projects.append(WxPySpecProject(filepath_or_file,
                                                 self._current_time()))
        self._update_config_files()
        if not self.test_mode:
            self._current().set_filepath(filepath_or_file)
            self._current().read()


    def save(self, test_data=None):
        target_project = self.projects[-1]
        if not self.test_mode:
            target_project.save()
        self.dirty_flag = False

    def save_as(self, filepath):
        target_project = self.projects[-1]
        target_project.last_used_time = self._current_time()
        if not self.test_mode:
            target_project.save(filepath)
            self._update_config_files()
        else:
            target_project.set_filepath(filepath)
        self.dirty_flag = False

    def can_save(self):
        return not self.is_default_file()

    def should_save(self):
        return self.dirty_flag

    def set_dirty_flag(self):
        self.dirty_flag = True

    def is_default_file(self):
        return self._current().is_default

    def is_auto_run(self):
        return self._current().auto_run

    def is_auto_reload(self):
        return self._current().auto_reload

    def is_fail_activate(self):
        return self._current().fail_activate

    def is_success_activate(self):
        return self._current().success_activate

    def get_function_hook(self):
        return self._current().function_hook

    def display_filename(self):
        if self._current().is_default:
            return "*new"
        if self.should_save():
            return "* %s *" % self.get_filepath()
        return self.get_filepath()

        return self.get_filepath()

    def get_filepath(self):
        return self._current().get_filepath()

    def last_used_time(self):
        return self._current().last_used_time

    def set_modules(self, specs):
        self._current().reset_specs(specs)

    def get_modules(self):
        return sorted(self._current().specs.values())
