# -*- coding: ascii -*-

"""PySpec User Interface for console.
"""

import sys
import time
import optparse
import pyspec
import pyspec.util
import pyspec.project
import pyspec.framework
from pyspec.embedded.setting import config
import pyspec.compat_ironpython as compat
import addin


__pyspec = 1
__all__ = ("CUISpecTestRunner",)

version = """PySpec Version %s
Copyright (c) 2006-2008 Shibukawa Yoshiki.""" % pyspec.__version__

class CUISetting(object):
    def __init__(self):
        self.verbosity = True
        self.color = False
        self.output_encoding = None
        self.show_legacy_data = False


class CUISpecResultRecorder(pyspec.framework.SpecResultRecorder):
    """This class prints formatted CUI test records to a stream.
    Used by CUITestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self):
        super(CUISpecResultRecorder, self).__init__()
        self.out = sys.stdout
        self.load_error_specs = set()
        self.load_errors = set()
        if config.cui.output_encoding:
            self.out = compat.get_console_encoder(config.cui.output_encoding)
        else:
            self.out = sys.stdout
        self.starttime = None

    def start_test(self, spec, contexts=None, data_args=None):
        super(CUISpecResultRecorder, self).start_test(spec, contexts, data_args)
        if not config.cui.verbosity:
            return
        if data_args:
            append_text = " <args=%s>" % " ".join(
                ("%s:%s" % (key, value) for key, value in data_args.iteritems()))
        else:
            append_text = ""
            if contexts is None:
                #print str(spec)
                self.out.write("\n" + spec.spec_name() + append_text)
            else:
                for context in contexts:
                    self.out.write("\n" + context.spec_name(context=True))
                self.out.write("\n    " + spec.spec_name() + append_text)
                self.out.write(" ... ")

    def add_success(self, spec):
        super(CUISpecResultRecorder, self).add_success(spec)
        if config.cui.color:
            self.out.write("\x1b[20m")
        if config.cui.verbosity:
            self.out.write("OK")
        else:
            self.out.write(".")
        if config.cui.color:
            self.out.write("\x1b[0m")

    def add_error(self, spec, err):
        super(CUISpecResultRecorder, self).add_error(spec, err)
        if config.cui.verbosity:
            self.out.write("Error")
        else:
            self.out.write("E")

    def add_failure(self, spec, err):
        super(CUISpecResultRecorder, self).add_failure(spec, err)
        if config.cui.verbosity:
            self.out.write("Failure")
        else:
            self.out.write("F")

    def add_ignore(self, spec, message=None):
        super(CUISpecResultRecorder, self).add_ignore(spec, message)
        if config.cui.verbosity:
            self.out.write("Ignored")
        else:
            self.out.write("I")

    def add_load_error(self, filepath, error_message):
        self.load_error_tests.add(filepath)
        self.load_errors.add("".join(error_message))

    def has_load_error(self):
        return len(self.load_errors) > 0

    def begin_test(self):
        self.starttime = time.time()

    def finish_test(self):
        takentime = time.time() - self.starttime
        self.print_errors()
        print self.separator2
        run = self.run_count
        print "Ran %d spec%s in %.3fs" % (run, run != 1 and "s" or "", takentime)
        if not self.was_successful():
            records = []
            failed, errored = map(len, (self.failures, self.errors))
            if failed:
                records.append("failures=%d" % failed)
            if errored:
                records.append("errors=%d" % errored)
            print "FAILED(%s)" % (", ".join(records))
        else:
            print "OK"

    def print_errors(self):
        print >>self.out, "\n"
        self.print_error_list('ERROR', self.errors)
        self.print_error_list('FAIL', self.failures)
        self.print_ignore_list()
        self.print_load_error()
        print >>self.out, "\n"

    def print_error_list(self, flavour, errors):
        for spec, err in errors:
            print >>self.out, self.separator1
            print >>self.out, "%s: %s" % (flavour,spec.spec_name(long=True))
            print >>self.out, self.separator2
            print >>self.out, err
            self.print_console(spec)

    def print_load_error(self):
        if self.load_error_specs:
            print >>self.out, self.separator1
            print >>self.out, "Load Error:"
            for spec in self.load_error_specs:
                print >>self.out, "  %s" % spec
            print >>self.out, self.separator2
            for message in self.load_errors:
                print >>self.out, message, "\n"
            print >>self.out, "No specs ran. Fix syntax errors first."

    def print_console(self, spec):
        if config.cui.verbosity and spec.console:
            print >>self.out, "Console:"
            for line in spec.console:
                print >>self.out, line[1],
        print >>self.out, ""

    def print_ignore_list(self):
        splitter = ''
        for spec, message in self.ignores:
            print >>self.out, splitter,
            print >>self.out, self.separator1
            print >>self.out, "Ignored Tests: %s" % spec.spec_name(long=True)
            print >>self.out, self.separator2
            if message:
                print >>self.out, "%s\n" % message
            else:
                print >>self.out, ''
            self.print_console(spec)
            splitter = '\n'


class CUISpecTestRunner(object):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    def __init__(self, auto=False):
        self.is_changed = False
        self.project = pyspec.project.PySpecProject()
        self.auto = auto
        self.kernel = pyspec.framework.PySpecKernel()
        self.addin = addin.CUIAddinManager(self.kernel)
        self.addin.load_addin()

        if auto:
            self._parse_options_in_auto_mode()
        else:
            self._parse_options_in_manual_mode()
        compat.patch_for_iron_python()

    def _run_option_parsing(self, auto_mode, use_ini_file=False):
        """Run option parsing."""
        usage = "usage: %prog [options] spec_modules..."
        parser = optparse.OptionParser(usage=usage, version=version)
        parser.add_option("-v", "--verbose", action="store_true",
                dest="verbose", default=True,
                help="make lots of information [default].")
        parser.add_option("-q", "--quiet", action="store_false",
                dest="verbose",
                help="ouput progress bar and result only")
        parser.add_option("-c", "--color", action="store_true",
                dest="color", default=False,
                help="color output")
        parser.add_option("-d", "--check-docstring", action="store_true",
                dest="check_docstring", default=False,
                help="verify test fails if the test has no docstring.")
        parser.add_option("-r", "--reset-legacy-data", action="store_true",
                dest="reset_legacy_data", default=False,
                help="reset all legacy test data.")
        parser.add_option("--show-legacy-data", action="store_true",
                dest="show_legacy_data", default=False,
                help="show recorded legacy test data.")
        parser.add_option("-g", "--language", metavar="LANG",
                default='en',
                help="change the report language.(sometimes it needs -e)\n"
                "supported code: %s" % ", ".join(config.language.support.keys()))

        if use_ini_file:
            parser.add_option("-l", "--load", metavar="PROJECT.pyspec",
                              help="load spec modules and settings from project file")
            parser.add_option("-s", "--save", metavar="PROJECT.pyspec",
                              help="save spec modules and settings to project file")
        parser.add_option("-e", "--encode", metavar="OUTPUT_CODEC",
                          help="set console encode")
        parser.add_option("--debug-pyspec", action="store_true",
                          dest="debug_pyspec", default=False,
                          help="show pyspec internal error traceback.")
        self.addin.call_event_handler("init_optparse", parser)
        options, specs = parser.parse_args()

        if options.encode is not None:
            self.project.cui_encoding = options.encode
            if use_ini_file and options.load is not None:
                self.is_changed = True

        config.framework.check_docstring = options.check_docstring
        config.framework.reset_legacy_data = options.reset_legacy_data
        config.environment.show_error = options.debug_pyspec

        config.language.set_language(options.language)
        cui_config = CUISetting()
        cui_config.verbosity = options.verbose
        cui_config.color = options.color
        cui_config.show_legacy_data = options.show_legacy_data
        cui_config.output_encoding = options.encode
        config.regist_config("cui", cui_config)

        if not auto_mode and len(specs) == 0:
            parser.print_help()
            print "\nThere is no spec."
            sys.exit(0)

        self.addin.call_event_handler("read_option", options, specs)

        return (options, specs)

    def _parse_options_in_auto_mode(self):
        """Parse test option in auto mode.
        Run spec with run_test() method, pyspec become auto mode.
        """
        options, specs = self._run_option_parsing(auto_mode=True)

    def _parse_options_in_manual_mode(self):
        """Read test option file.
        Run spec with cuipyspec, pyspec become manual mode.
        """
        options, specs = self._run_option_parsing(auto_mode=False,
                                                  use_ini_file=True)

        if options.load is not None:
            self.project.read(options.load)
            if options.save is not None:
                self.project.set_filepath(options.save)
                self.is_changed = True
        elif options.save is not None:
            self.project.set_filepath(options.save)
            self.is_changed = True
        default_count  = len(self.project.specs)
        self.project.add_specs(specs)
        if default_count != len(self.project.specs) and default_count != 0:
            self.is_changed = True

    def run(self):
        """Run the given specs.
        """
        recorder = CUISpecResultRecorder()

        config.load_legacy_test_data()
        if config.cui.show_legacy_data:
            self._show_legacy_data(recorder.out)
            return None

        if self.auto:
            self.kernel.set_all_modules()
        else:
            for filepath in self.project.specs.itervalues():
                self.kernel.modules.load_module(filepath)

        if recorder.has_load_error():
            recorder.print_errors()
            return

        self.addin.call_event_handler("on_run_test")
        recorder.begin_test()

        for spec_module in self.kernel.modules.get_modules("pyspec"):
            spec_module.run(recorder)

        recorder.finish_test()
        self.addin.call_event_handler("on_finish_test", recorder)

        config.save_legacy_test_data()

        if self.is_changed:
            self.project.save()
        return recorder

    def _show_legacy_data(self, cout):
        keys = sorted(config.runtime.legacy_data.keys())
        current_module = None
        current_class = None
        current_method = None
        current_variable = None

        for key in keys:
            module, class_name, method, variable = key[0:4]
            if module != current_module:
                print >>cout, self._create_title("module: %s" % module, 1)
                current_module = module
            if class_name != current_class:
                print >>cout, self._create_title("class: %s" % class_name, 2)
                current_class = class_name
            if method != current_method:
                print >>cout, self._create_title("method: %s" % method, 3)
                current_method = method
            if variable != current_variable:
                print >>cout, self._create_title("variable: %s" % variable, 4)
                current_variable = variable
            for call in config.runtime.legacy_data[key]:
                call_repr = pyspec.util.create_method_repr(call[0], *call[1])
                if call[2] is not None:
                    print >>cout, '%s => %s' % (call_repr, call[3])
                else:
                    print >>cout, '%s' % call_repr

    def _create_title(self, string, level):
        deco1 = '=' * len(string)
        deco2 = '-' * len(string)
        if level == 1:
            return '%s\n%s\n%s\n' % (deco1, string, deco1)
        elif level == 2:
            return '%s\n%s\n%s\n' % (deco2, string, deco2)
        elif level == 3:
            return '\n%s\n%s\n' % (string, deco1)
        else:
            deco = '-' * len(string)
            return '\n%s\n%s\n' % (string, deco2)

