# -*- coding: ascii -*-

__pyspec = 1

import os, time
import pyspec
import pyspec.tempita as tempita
from pyspec.tempita import bunch
import traceback
from pyspec.cui.api import *

class reSTFormatter(object):
    def __init__(self, addin_manager):
        self.current_dir = addin_manager.addin_dir
        self.output_folder = None
        self.modules = addin_manager.get_module_observer()

    def set_option(self, option):
        self.output_folder = option.reST

    def generate(self, recorder):
        if self.output_folder is None:
            return
        summary = self._create_summary(recorder)
        result = bunch(summary=summary,modules=[])
        module_map = {}
        self._create_module_bunch(module_map, result)
        self._create_result_record(module_map, recorder.failures, "failures")
        self._create_result_record(module_map, recorder.errors, "errors")
        self._create_file("summary.rst", result)

    def _create_summary(self, recorder):
        summary = bunch(ran=recorder.run_count,
                        error=len(recorder.errors),
                        failure=len(recorder.failures),
                        now=time.ctime(),
                        version=pyspec.__version__,
                        message=bunch())
        if summary.error == 0:
            summary.message["error"]="There is no error."
        elif summary.error == 1:
            summary.message["error"]="There is 1 error."
        else:
            summary.message["error"]="There is %d errors." % summary.error

        if summary.failure == 0:
            summary.message["failure"]="There is no failure."
        elif summary.failure == 1:
            summary.message["failure"]="There is 1 failure."
        else:
            summary.message["failure"]="There is %d failures." % summary.failure
        return summary

    def _create_module_bunch(self, module_map, result):
        for module in self.modules.get_modules("pyspec"):
            name = module.short_name()
            if name == "__main__":
                name = os.path.splitext(module.target().__file__)[0]
            print_name = "%s module\n%s" % (name, "-"*(len(name)+7))
            module_bunch = tempita.bunch(name=print_name,
                                         failures=[],
                                         errors=[],
                                         success=[])
            module_map[module] = module_bunch
            result.modules.append(module_bunch)

    def _create_result_record(self, module_map, target, entry):
        for spec, error in target:
            module_bunch = module_map.get(spec.module())
            if module_bunch is None:
                continue
            module_bunch[entry].append(bunch(
                                         contexts=spec.contexts,
                                         spec_name=spec.spec_name(long=True),
                                         error_message=self._add_indent(error)))

    def _create_error_info(self, recorder, module_map):
        for spec, error in recorder.failures:
            module_bunch = module_map.get(spec.module())
            if module_bunch is None:
                continue
            module_bunch.failures.append(bunch(
                                         contexts=spec.contexts,
                                         spec_name=spec.spec_name(long=True),
                                         error_message=self._add_indent(error)))

    def _create_file(self, filename, variables):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        template_path = os.path.join(self.current_dir, filename)
        template = tempita.Template.from_filename(template_path)

        filepath = os.path.join(self.output_folder, filename)
        output_file = open(filepath, "w")
        output_file.write(template.substitute(variables))
        output_file.close()

    def _add_indent(self, source, indent=8):
        spacer = " " * indent
        lines = []
        for line in source.splitlines():
            lines.append("%s%s" % (spacer, line))
        return "\n".join(lines)


@entry_point
def init_reST_formatter_addin(addin_manager):
    return reSTFormatter(addin_manager)


@event_handler("init_optparse")
def add_option(formatter, optparser):
    optparser.add_option("--reST_report", metavar="dirname",
                         dest="reST", default=None,
                         help="generate reST format report")


@event_handler("read_option")
def read_option(formatter, option, specs):
    formatter.set_option(option)


@event_handler("on_finish_test")
def write_reST_result(formatter, recorder):
    formatter.generate(recorder)
