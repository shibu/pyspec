# -*- coding: ascii -*-

"""PySpec helper class that treats test options.
"""

import ConfigParser
import pyspec.util

__pyspec = 1


class PySpecProject(object):
    def __init__(self, file_or_filepath = None, does_read=True):
        self._clear_all()
        self.filepath = "new.pyspec"
        if file_or_filepath is not None:
            if does_read:
                self.read(file_or_filepath)
            else:
                self.set_filepath(file_or_filepath)

    def _clear_all(self):
        self.specs = {}
        self.is_default = True
        self.cui_encoding = "utf8"
        self.function_hook = "trace"

    def reset_filepath(self, filepath=None):
        if filepath != None and filepath != self.filepath:
            if not filepath.endswith(".pyspec"):
                filepath = filepath + ".pyspec"
            self.is_default = False
            self.filepath = filepath

    def set_filepath(self, path):
        self.is_default = False
        self.filepath = path

    def get_filepath(self):
        return self.filepath

    def read(self, file_or_filepath=None):
        parser = ConfigParser.SafeConfigParser()
        if file_or_filepath is None:
            file_or_filepath = self.get_filepath()
        is_test_mode = not isinstance(file_or_filepath, basestring)
        if is_test_mode:
            readpath = None
            parser.readfp(file_or_filepath)
        else:
            self.reset_filepath(file_or_filepath)
            readpath = self.get_filepath()
            print "read: %s" % readpath
            if readpath == "new.pyspec":
                raise
            parser.read(readpath)
        self.specs = {}
        try:
            specs = dict(parser.items("Specs"))
            for name, path in specs.iteritems():
                if readpath is not None:
                    self.specs[name] = pyspec.util.absolute_path(readpath, path)
                else:
                    self.specs[name] = path
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            pass
        self._read_str_option(parser, "Config", "cui_encoding")
        self._read_str_option(parser, "Config", "function_hook")
        self._read_template(parser)
        self.is_default = False

    def _read_str_option(self, parser, section, name):
        try:
            setattr(self, name, parser.get(section, name))
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            print "read option error: %s:%s" % (section, name)

    def _read_bool_option(self, parser, section, name):
        try:
            setattr(self, name, parser.get(section, name)=="True")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            print "read option error: %s:%s" % (section, name)

    def _read_template(self, parser):
        pass

    def save(self, file_or_filepath=None):
        if isinstance(file_or_filepath, basestring):
            self.reset_filepath(file_or_filepath)
            writepath = self.get_filepath()
            file_obj = file(writepath, "w")
        elif file_or_filepath is None:
            writepath = self.get_filepath()
            file_obj = file(writepath, "w")
        else:
            writepath = None
            file_obj = file_or_filepath
        print writepath
        parser = ConfigParser.SafeConfigParser()
        parser.add_section("Config")
        parser.set("Config", "cui_encoding", self.cui_encoding)
        parser.set("Config", "function_hook", self.function_hook)
        parser.add_section("Specs")
        for name, value in self.specs.iteritems():
            path = pyspec.util.relative_path(writepath, value)
            parser.set("Specs", name, path)
        self._save_template(parser)
        print "save: %s" % writepath
        parser.write(file_obj)
        self.is_default = False

    def _save_template(self, parser):
        pass

    def reset_specs(self, specs):
        self.specs = {}
        self.add_specs(specs)

    def add_specs(self, specs):
        for spec in specs:
            self._add_spec(spec)

    def _add_spec(self, spec):
        import os
        basename = os.path.basename(spec)
        modulename, extname = os.path.splitext(basename)
        if extname != ".py":
            return
        self.specs[modulename] = os.path.abspath(spec)
