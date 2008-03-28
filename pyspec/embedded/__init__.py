# -*- coding: ascii -*-

"""PySpec Embedded - Behavior Driven Development Framework -.

This package only have some classes and functions to write a simple
test and debug.



This software is inspired by unittest module.
I thank Mr.Steve Purcell for his work.

And I must say 'thank you' to Mr. Masaru Ishii too.
He popularized unit test in Japan.

PySpec License
==============

License:  The MIT License
Copyright (c) 2007 Shibukawa Yoshiki

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

__docformat__ = 'restructuredtext en'

#: The version of pyspec
__version__ = '0.54-pre'
#: The primary author of pyspec
__author__ = 'Shibukawa Yoshiki <yoshiki at shibu.jp>'
#: The URL for pyspec's project page
__url__ = 'http://www.codeplex.com/pyspec'
#: The license governing the use and distribution of pyspec"""
__license__ = 'MIT License'

__pyspec = 1

import compat_ironpython

from assertions import About, VerifierBase, regist_test_verifier
from dprint import dprint
import setting

config = setting.PySpecConfig()
