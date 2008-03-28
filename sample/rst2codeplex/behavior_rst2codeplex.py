# -*- coding: ascii -*-

import sys, os
parent_path = os.path.split(os.path.abspath(".."))[0]
if parent_path not in sys.path:
   sys.path.insert(0, parent_path)

from rst2codeplex import Writer, CodePlexTranslator
from pyspec import *
from pyspec.legacycode import test_proxy

class Behavior_rst2codeplex(object):
    source_title = """
==========
Test Title
==========
"""

    @context(group=1)
    def Title_source(self):
        self.result = entry_point(self.source_title)

    @spec(group=1)
    def can_convert_to_wiki1(self):
        About(self.result).should_include("! Test Title")

    @spec(group=2)
    def method_call_should_not_changed_for_title(self):
        print entry_point(self.source_title, use_proxy=True)

    source_subtitle = """
==========
Test Title
==========

--------
SubTitle
--------
"""
    @context(group=3)
    def Subtitle_source(self):
        self.result = entry_point(self.source_subtitle)

    @spec(group=3)
    def can_convert_to_wiki2(self):
        About(self.result).should_include("!! SubTitle")
        About(self.result).should_include("{anchor:test-title}")

    @spec(group=4)
    def method_call_should_not_changed_for_subtitle(self):
        print entry_point(self.source_subtitle, use_proxy=True)

    source_subsubtitle = """
==========
Test Title
==========

--------
SubTitle
--------

SubSubTitle
***********
"""
    @context(group=5)
    def Subsubtitle_source(self):
        self.result = entry_point(self.source_subsubtitle)

    @spec(group=5)
    def can_convert_to_wiki3(self):
        About(self.result).should_include("!!! SubSubTitle")

    @spec(group=6)
    def method_call_should_not_changed_for_subsubtitle(self):
        print entry_point(self.source_subsubtitle, use_proxy=True)

    source_subsubsubtitle = """
==========
Test Title
==========

--------
SubTitle
--------

SubSubTitle
***********

SubSubSubTitle
--------------
"""
    @context(group=7)
    def Subsubsubtitle_source(self):
        self.result = entry_point(self.source_subsubsubtitle)

    @spec(group=7)
    def can_convert_to_wiki4(self):
        About(self.result).should_include("!!!! SubSubSubTitle")

    @spec(group=8)
    def method_call_should_not_changed_for_subsubsubtitle(self):
        print entry_point(self.source_subsubsubtitle, use_proxy=True)

    source_bulleted_list = """
==================
Test Bulleted List
==================

* List Level 1
   * List Level 2

"""
    @context(group=9)
    def Bulleted_list_source(self):
        self.result = entry_point(self.source_bulleted_list)

    @spec(group=9)
    def can_convert_to_wiki5(self):
        About(self.result).should_include("* List Level 1")
        About(self.result).should_include("** List Level 2")

    @spec(group=10)
    def method_call_should_not_changed_for_bulleted_list(self):
        print entry_point(self.source_bulleted_list, use_proxy=True)

    source_numbered_list = """
==================
Test Numbered List
==================

1. List Level 1

   1. List Level 2

"""
    @context(group=11)
    def Numbered_list_source(self):
        self.result = entry_point(self.source_numbered_list)

    @spec(group=11)
    def can_convert_to_wiki6(self):
        About(self.result).should_include("# List Level 1")
        About(self.result).should_include("## List Level 2")

    @spec(group=12)
    def method_call_should_not_changed_for_numbered_list(self):
        print entry_point(self.source_numbered_list, use_proxy=True)

    source_text_formatter = """
===================
Test Text Fromatter
===================

**bold**

*italics*

``inline literal``
"""
    @context(group=13)
    def Text_formatter_source(self):
        self.result = entry_point(self.source_text_formatter)

    @spec(group=13)
    def can_convert_to_wiki7(self):
        About(self.result).should_include("*bold*")
        About(self.result).should_include("_italics_")
        About(self.result).should_include("{{inline literal}}")

    @spec(group=14)
    def method_call_should_not_changed_for_text_formatter(self):
        print entry_point(self.source_text_formatter, use_proxy=True)

    source_paragraph = """
==============
Test Paragraph
==============

paragraph1

paragraph2
"""
    @context(group=15)
    def Paragraph_source(self):
        self.result = entry_point(self.source_paragraph)

    @spec(group=15)
    def can_convert_to_wiki8(self):
        About(self.result).should_include("\nparagraph1\n")
        About(self.result).should_include("\nparagraph2\n")
        About(self.result).should_not_include("<p")

    @spec(group=16)
    def method_call_should_not_changed_for_paragraph(self):
        print entry_point(self.source_paragraph, use_proxy=True)

    source_literal_block = """
==================
Test Literal Block
==================

sample::

    class SamplePythonClass(object):
        def __init__(self):
            pass

"""
    @context(group=17)
    def Literal_blcok_source(self):
        self.result = entry_point(self.source_literal_block)

    @spec(group=17)
    def can_convert_to_wiki9(self):
        About(self.result).should_include("{{")
        About(self.result).should_include("}}")
        About(self.result).should_not_include("<pre")

    @spec(group=18)
    def method_call_should_not_changed_for_literal_block(self):
        print entry_point(self.source_literal_block, use_proxy=True)

    source_table1 = """
==========
Test Table
==========

========= =====================================
Parameter Description
========= =====================================
key       Set the spec method's parameter name.
group     Set the data provider method's group.
========= =====================================

"""
    @context(group=19)
    def Table_source(self):
        self.result = entry_point(self.source_table1)

    @spec(group=19)
    def can_convert_to_wiki10(self):
        About(self.result).should_include("| *Parameter* |")
        About(self.result).should_include("| key |")
        About(self.result).should_not_include("<table")

    @spec(group=20)
    def method_call_should_not_changed_for_table(self):
        print entry_point(self.source_table1, use_proxy=True)

    source_docinfo = """
==========
Test Table
==========

:Author: Shibukawa Yoshiki
:Contact: yoshiki at shibu.jp
:Copyright: This document has been placed in the public domain.
"""
    @context(group=21)
    def Docinfo_source(self):
        self.result = entry_point(self.source_docinfo)

    @spec(group=21)
    def can_convert_to_wiki11(self):
        About(self.result).should_include("| *Author* |")
        About(self.result).should_include("| Shibukawa Yoshiki |")
        About(self.result).should_not_include("<table")

    @spec(group=22)
    def method_call_should_not_changed_for_docinfo(self):
        print entry_point(self.source_docinfo, use_proxy=True)

    source_titles_with_contents = """
==========
Test Title
==========

.. contents::

--------
SubTitle
--------

SubSubTitle
***********

SubSubSubTitle
--------------
"""
    @context(group=23)
    def Contents_source(self):
        self.result = entry_point(self.source_titles_with_contents)

    @spec(group=23)
    def can_convert_to_wiki12(self):
        About(self.result).should_include("[SubTitle|#subtitle]\n")
        About(self.result).should_include("[SubSubTitle|#subsubtitle]\n")
        About(self.result).should_include("[SubSubSubTitle|#subsubsubtitle]\n")

    @spec(group=24)
    def method_call_should_not_changed_for_contents(self):
        print entry_point(self.source_titles_with_contents, use_proxy=True)

    source_field_list = """
===============
Test Field List
===============

:note: This is note.
"""
    @context(group=25)
    def Field_list_source(self):
        self.result = entry_point(self.source_field_list)

    @spec(group=25)
    def can_convert_to_wiki13(self):
        About(self.result).should_include("| *note:* |")

    @spec(group=26)
    def method_call_should_not_changed_for_field_list(self):
        print entry_point(self.source_field_list, use_proxy=True)

    source_escape = """
===========
Test Escape
===========

<, >, @, &
"""
    @context(group=27)
    def Escape_character_in_html_source(self):
        self.result = entry_point(self.source_escape)

    @spec(group=27)
    def doews_not_convert_to_wiki14(self):
        About(self.result).should_include("<")
        About(self.result).should_include(">")
        About(self.result).should_include("@")
        About(self.result).should_include("&")

    @spec(group=28)
    def method_call_should_not_changed_for_escaping_string(self):
        print entry_point(self.source_escape, use_proxy=True)


#========================= Dummy Entry Point =========================

def TranslatorWithProxy(document):
    translator = CodePlexTranslator(document)
    return test_proxy(translator, check_return=False)


def entry_point(source, use_proxy=False):
    from docutils.core import publish_string
    if use_proxy:
        return publish_string(source, writer_name="codeplex",
                writer=Writer(translator=TranslatorWithProxy))
    return publish_string(source, writer_name="codeplex",
            writer=Writer(translator=CodePlexTranslator))


if __name__ == "__main__":
    run_test()
