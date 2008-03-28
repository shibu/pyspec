# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *

import StringIO
import pyspec.project


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


class PySpecProject_read_Behavior(object):
    @context
    def A_project_object(self):
        file_obj = StringIO.StringIO(sample_project_file)
        self.project = pyspec.project.PySpecProject(file_obj)

    @spec
    def should_read_test_options(self):
        About(self.project.cui_encoding).should_be_true()
        About(self.project.function_hook).should_equal("trace")

    @spec(expected=AttributeError)
    def should_not_read_only_common_options(self):
        self.project.auto_run

    @spec
    def should_read_spec_file_list(self):
        About(self.project.specs["test_pyspec"]).should_equal(
                                  "D:\\home\\shibu\\pyspec\\pyspec.py")
    @spec
    def should_add_specs(self):
        self.project.add_specs(["D:\\home\\shibu\\pyspec\\pyspec2.py"])
        About(self.project.specs).should_include("pyspec2")

    @spec
    def should_remain_spec_after_adding_new_spec(self):
        self.project.add_specs(["D:\\home\\shibu\\pyspec\\pyspec2.py"])
        About(self.project.specs).should_include("test_pyspec")

    @spec
    def should_reset_specs(self):
        self.project.reset_specs(["D:\\home\\shibu\\pyspec\\pyspec2.py"])
        About(self.project.specs).should_include("pyspec2")

    @spec
    def should_not_remain_spec_after_reseting_new_spec(self):
        self.project.reset_specs(["D:\\home\\shibu\\pyspec\\pyspec2.py"])
        About(self.project.specs).should_not_include("test_pyspec")

if __name__ == "__main__":
    run_test()
