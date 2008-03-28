# -*- coding: utf_8 -*-

def generate(lang):
    """各言語のHello World!を返します."""
    if lang == "Python":
        return generate_python()
    raise KeyError

def generate_python():
    """PythonのHello World!を返します."""
    return "print 'Hello World!'"
