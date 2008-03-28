# -*- coding: utf-8 -*-

import sys, os
parent_path = os.path.split(os.path.abspath("."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from pyspec import *
from pyspec.mockobject import *
import pyspec.framework
import pyspec.embedded.setting as setting


class Behavior_Setting_for_Localization(object):
    @context(group=1)
    def a_default_config(self):
        self.config = setting.PySpecConfig()

    @spec(group=1)
    def should_have_english_locale_as_default(self):
        About(self.config.language.code).should_equal('en')

    @spec(group=1)
    def should_have_supported_language(self):
        About(self.config.language.support).should_include('en')
        About(self.config.language.support).should_include('ja')

    @context(group=2)
    def a_config_that_was_set_valid_language(self):
        self.config = setting.PySpecConfig()
        self.config.language.set_language('ja')

    @spec(group=2)
    def can_accept_it(self):
        About(self.config.language.code).should_equal('ja')

    @context(group=3)
    def a_config_that_was_set_invalid_language(self):
        self.config = setting.PySpecConfig()
        # pyspec can't accept tlhIngan Hol!
        self.config.language.set_language('tlh')

    @spec(group=3)
    def should_not_change_language(self):
        About(self.config.language.code).should_equal('en')

    @context(group=4)
    def should_equal_fail_message_in_english(self):
        config = setting.PySpecConfig()
        self.english_message = config.language.get('should_equal',
                               'fail', variable_name='age',
                               expected_value='27',
                               actual_value='29')

    @spec(group=4)
    def pyspec_can_generete_it(self):
        About(self.english_message).should_equal('age should equal 27, but was 29.')


if __name__ == "__main__":
    run_test()


