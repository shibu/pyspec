# -*- coding: ascii -*-

"""
"""

import os
import imp
import sys
import copy
import pickle
import string
import languages.en


class PySpecFrameworkOption(object):
    def __init__(self):
        #: This option controls pre post conditions
        self.dbc_prepost_option = False
        #: This option controls invariant conditions
        self.dbc_invariant_option = False
        #main = sys.modules["__main__"]
        #self.cache_file_name = main.__file__ + ".cache"
        self.cache_file_name = sys.argv[0] + ".cache"
        self.check_docstring = False
        #: Reset all legacy data
        self.reset_legacy_data = False


class PySpecRuntimeOption(object):
    def __init__(self, framework_option):
        self.legacy_data = {}
        self.module_name = None
        self.class_name = None
        self.method_name = None
        self.recording_flag = False
        self.indexes = {}
        self.ignore_stack = False
        self.report_out = None
        self._framework_option = framework_option

    def start_spec(self, spec_method_name=None):
        self.method_name = spec_method_name
        self.recording_flag = False
        self.indexes = {}

    def _recording_key(self, variable_name):
        index = self.indexes.setdefault(variable_name, 0)
        self.indexes[variable_name] = index + 1
        return (self.module_name, self.class_name,
                self.method_name, variable_name, index)

    def _reference_key(self, variable_name):
        index = self.indexes.setdefault(variable_name, 0)
        return (self.module_name, self.class_name,
                self.method_name, variable_name, index)

    def _has_key(self, key):
        return key in self.legacy_data

    def get_recorded_value(self, variable_name, value, reset=False):
        key = self._recording_key(variable_name)
        reset = reset or self._framework_option.reset_legacy_data
        if reset or key not in self.legacy_data:
            self.legacy_data[key] = value
            return value, True
        return self.legacy_data[key], False


class PySpecNatinalLanugageSupport(object):
    def __init__(self):
        self.code = 'en'
        self.support = {}
        current_dir = os.path.abspath(os.path.split(__file__)[0])
        locale_dir = os.path.join(current_dir, 'languages')
        for file_name in os.listdir(locale_dir):
            if file_name.endswith('.py') and file_name != '__init__.py':
                filepath = os.path.join(locale_dir, file_name)
                self.support[file_name[:-3]] = {"path":filepath, "words":None}
        self.words = self._make_template(languages.en)
        self.support["en"]["words"] = copy.copy(self.words)

    def set_language(self, language_code):
        if language_code not in self.support:
            return
        if language_code == self.code:
            return
        self.code = language_code
        if self.support[language_code]["words"] is None:
            filepath = self.support[language_code]["path"]
            (path, name) = os.path.split(filepath)
            (name, ext) = os.path.splitext(name)
            (file, filename, data) = imp.find_module(name, [path])
            module = imp.load_module(name, file, filepath, data)
            compiled_words = self._make_template(module)
            self.support[language_code]["words"] = compiled_words
        else:
            compiled_words = self.support[language_code]["words"]
        for key, word in compiled_words.iteritems():
            self.words[key] = word

    def get(self, message_code, message_type, **kwargs):
        template = self.words[(message_code, message_type)]
        return template.safe_substitute(kwargs)

    def _make_template(self, module):
        templates = {}
        for objname in dir(module):
            if objname.startswith('__'):
                continue
            obj = getattr(module, objname)
            if not isinstance(obj, dict):
                continue
            for key, template in obj.iteritems():
                templates[(objname, key)] = string.Template(template)
        return templates



class PySpecConfig(object):
    class PySpecEnvironmentOption(object):
        def __init__(self):
            self.show_error = False

    def __init__(self):
        self.environment = self.PySpecEnvironmentOption()
        self.framework = PySpecFrameworkOption()
        self.runtime = PySpecRuntimeOption(self.framework)
        self.language = PySpecNatinalLanugageSupport()
        self._configs = {"framework":[], "runtime":[]}

    def load_legacy_test_data(self):
        if self.framework.reset_legacy_data:
            return
        if os.path.exists(self.framework.cache_file_name):
            self.runtime.legacy_data = pickle.load(
                    file(self.framework.cache_file_name))

    def save_legacy_test_data(self):
        #print self.runtime.legacy_data
        if self.runtime.legacy_data:
            output_file = file(self.framework.cache_file_name, "w")
            try:
                pickle.dump(self.runtime.legacy_data, output_file)
            except:
                output_file.close()
                os.remove(self.framework.cache_file_name)
                raise

    def regist_config(self, name, obj):
        if name in ("framework", "runtime"):
            option = getattr(self, name)
            self._configs[name].append(option)
            setattr(self, name, obj)
        elif name == "environment":
            raise NameError("cannot override envirionment option")
        else:
            self._configs.setdefault(name, []).append(obj)

    def remove_config(self, name):
        if name in ("framework", "runtime"):
            setattr(self, name, self._configs[name].pop())
        elif name == "environment":
            raise NameError("cannot remove envirionment option")
        else:
            delattr(self, name)

    def __getattribute__(self, name):
        try:
            return super(PySpecConfig, self).__getattribute__(name)
        except AttributeError:
            return self._configs[name][-1]


config = PySpecConfig()
