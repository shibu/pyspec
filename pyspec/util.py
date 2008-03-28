# -*- coding: ascii -*-

__pyspec = 1


import os
import sys
import types
import inspect
import traceback

from compat_ironpython import (ConsoleHook, STDOUT, STDERR,
                               CONTEXT_INFO, DATA_PROVIDER_INFO, REPORT_OUT)


class Struct(dict):
    def __getattribute__(self, name):
        try:
            attr = super(Struct, self).__getattr__(name)
        except AttributeError:
            if not super(Struct, self).has_key(name):
                raise AttributeError,name
            attr = super(Struct, self).get(name)
        return attr

    def __setattr__(self, name, value):
        super(Struct, self).__setitem__(name, value)

    def __delattr__(self, name):
        super(Struct, self).__delitem__(name)


def format_html(xml, title = "", header = None, footer = None,
               stylesheet = None):
    """Create HTML from nested strings and dictionaries."""
    import StringIO
    out = StringIO.StringIO()
    head = [u"head",
                [u"meta",
                    {u"http-equiv":u"Content-Type",
                     u"content":u"text/html;charset=utf_8"}],
                [u"title", title]]
    if stylesheet:
        head.append([u"link", {u"href":stylesheet,
                               u"rel":u"stylesheet",
                               u"type":u"text/css"}])
    body = [u"body"]
    if header != None:
        body.append(header)
    body = body + xml
    if footer != None:
        body.append(footer)
    html = [u"html", head, body]
    format_xml(html, out, u"", True)
    return out.getvalue()


def format_xml(xml, out, indent = "", oldstyle=False):
    """Create XML from nested strings and dictionaries."""
    from re import compile
    from cgi import escape
    splitter = compile(u"(.*)\.(.*)")
    if isinstance(xml, list):
        next = 1
        element = xml[0]
        attributes = u""
        match = splitter.match(element)
        if match:
            element = match.groups()[0]
            attributes = u' class="%s"' % match.groups()[1]
        if len(xml) > 1 and isinstance(xml[1], dict):
            attr_list = []
            for attr in xml[1].iteritems():
                if attr[1] is not None:
                    attr_list.append(u'%s="%s"' % (escape(str(attr[0])),
                                                   escape(str(attr[1]))))
                else:
                    attr_list.append(escape(attr[0]))
            attributes = attributes + u" " + u" ".join(attr_list)
            next = next + 1
        if len(xml) <= next:
            if oldstyle:
                out.write(u"%s<%s%s>" % (indent, element, attributes))
            else:
                out.write(u"%s<%s%s/>" % (indent, element, attributes))
        elif len(xml) == next + 1 and not isinstance(xml[next], list):
            out.write(u"%s<%s%s>" % (indent, element, attributes))
            format_xml(xml[next], out, u"", oldstyle)
            out.write(u"%s</%s>" % (u"", element))
        else:
            out.write(u"%s<%s%s>\n" % (indent, element, attributes))
            for i in xrange(next, len(xml)):
                format_xml(xml[i], out, indent + "  ", oldstyle)
                out.write("\n")
            out.write(u"%s</%s>" % (indent, element))
    else:
        result_text = escape(unicode(xml)).replace(u"&amp;nbsp;", u"&nbsp;")
        out.write(indent + result_text)


def exc_info_to_string(err):
    """Converts a sys.exc_info()-style tuple of values into a string."""
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and is_relevant_tb_level(tb):
        tb = tb.tb_next
    if exctype is AssertionError:
        length = count_relevant_tb_levels(tb)
        return ''.join(traceback.format_exception(exctype, value, tb, length))
    return ''.join(traceback.format_exception(exctype, value, tb))


def is_relevant_tb_level(tb):
    return tb.tb_frame.f_globals.has_key('__pyspec')


def count_relevant_tb_levels(tb):
    length = 0
    while tb and not is_relevant_tb_level(tb):
        length += 1
        tb = tb.tb_next
    return length


def defined_file_info(target):
    filename = inspect.getsourcefile(target)
    linenum = inspect.getsourcelines(target)
    return "%s(%d)"% (os.path.basename(filename), linenum[1])


def split_path(path, no_drive=False):
    result = []
    while True:
        head, tail = os.path.split(path)
        if head == "":
            result.insert(0, tail)
            break
        path = head
        if tail != "":
            result.insert(0, tail)
        elif os.path.split(head)[0] == head:
            break
    try:
        if not no_drive and sys.platform == "win32":
            driveletter = os.path.splitdrive(path)[0]
            if driveletter != "":
                result.insert(0, driveletter + "\\")
    except IndexError:
        pass
    return result


def relative_path(from_path, to_path):
    if from_path is None:
        return to_path
    from_list = split_path(from_path)[:-1]
    to_list = split_path(to_path)
    while True:
        try:
            if from_list[0] != to_list[0]:
                break
            del from_list[0]
            del to_list[0]
        except IndexError:
            break
    if len(from_list) == 0:
        to_list.insert(0, ".")
    else:
        for parent in from_list:
            to_list.insert(0, "..")
    return os.path.join(*to_list)


def absolute_path(from_path, relative_path):
    from_list = split_path(from_path, no_drive=False)[:-1]
    result = split_path(relative_path, no_drive=True)
    while True:
        if result[0] == "..":
            del result[0]
            del from_list[-1]
        elif result[0] == ".":
            del result[0]
            break
        else:
            break
    result = from_list + result
    if from_path.startswith("/"):
        return os.path.join("/", *result)
    return os.path.join(*result)

def home_path(filename):
    # this code copy from user.py
    import os
    home = os.curdir
    if 'HOME' in os.environ:
        home = os.environ['HOME']
    elif os.name == 'posix':
        home = os.path.expanduser("~/")
    elif os.name == 'nt':
        if 'HOMEPATH' in os.environ:
            if 'HOMEDRIVE' in os.environ:
                home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
            else:
                home = os.environ['HOMEPATH']
    return os.path.join(home, filename)


def pyspec_file_path(*filenames):
    import pyspec, os
    prefix = os.path.abspath(os.path.dirname(pyspec.__file__))
    return os.path.join(prefix, *filenames)


def explore_module(module):
    result = Struct({"classobj":{}, "func":{}})
    for name in dir(module):
        obj = getattr(module, name)
        if type(obj) in (types.FunctionType, types.BuiltinFunctionType):
            result.func[name] = obj
        if type(obj) in (types.TypeType, types.ClassType):
            result.classobj[name] = explore_class(obj)
    if has_attribute:
        self.triggers.append(TestModuleTrigger(test_module))


def explore_class(classobj):
    result = Struct({"obj":classobj, "staticmethod":{},
                     "classmethod":{}, "method":{}})
    for name in dir(classobj):
        obj = getattr(classobj, name)
        if type(obj) is types.FunctionType:
            result.staticmethod[name] = obj
        elif type(obj) is types.MethodType:
            if obj.im_class is types.TypeType:
                result.classmethod[name] = obj
            else:
                result.method[name] = obj
    return result


def sort_by_index(a, b):
    return cmp(a.find_aspect("pyspec").index(), b.find_aspect("pyspec").index())


class IsolatedStackFrame(object):
    """Function call information.

    - function type:
        class_name, instance_name, instance_id = None
        name() = method_name
    - class method:
        class_name != None
        instance_name, instance_id = None
        name() != method_name
    - instance method:
        class_name, instance_name, instance_id != None
        name() != method_name
    """
    __slots__ = ('method_name', 'instance_name', 'instance_id',
                 'class_name', 'module_name', 'event_code', 'is_pyspec')
    def __init__(self, event_code, frame, arg):
        if event_code in (3, 4, 5):
            self.method_name = "%s()" % arg.__name__
        else:
            self.method_name = "%s()" % frame.f_code.co_name
        self.instance_name = None
        self.class_name = None
        self.module_name = str(frame.f_globals.get("__name__"))
        self.instance_id = None
        self.event_code = event_code
        self.is_pyspec = frame.f_globals.has_key("__pyspec")
        if event_code in (0, 3):
            try:
                receiver = frame.f_locals.get("self")
                if receiver is None:
                    receiver = frame.f_locals.get("cls")
                    if receiver is None:
                        return
                if type(receiver) in (types.TypeType, types.ClassType):
                    self.class_name = receiver.__name__
                    return
                else:
                    self.class_name = receiver.__class__.__name__
                    self.instance_id = id(receiver)
                    is_find = False
                    last_frame = frame.f_back
                    if last_frame is not None:
                        for name, obj in last_frame.f_locals.iteritems():
                            if self.instance_id == id(obj):
                                self.instance_name = name
                                return
                        if not is_find:
                            last_self = last_frame.f_locals.get("self")
                            if last_self is None:
                                return
                            for name in dir(last_self):
                                if result.instance_id == id(getattr(last_self, name)):
                                    result.instance_name = name
                                    return
            except:
                pass

    def __repr__(self):
        return "<IsolatedStackFrame object at 0x%x: %s>" % (id(self),
                                                       self.get_instance_name())

    def get_instance_name(self):
        if self.instance_id is None:
            return None
        elif self.instance_name is not None:
            return "%s : %s" % (self.instance_name, self.class_name)
        else:
            return "'tmp' : %s" % self.class_name

    def name(self):
        if self.instance_id is None:
            if self.class_name is None:
                return self.method_name
            elif self.method_name.endswith("__init__()"):
                return "%s <<create>>" % self.class_name
            else:
                return "%s.%s :classmethod" % (self.class_name,
                                               self.method_name)
        else:
            return "%s.%s" % (self.class_name, self.method_name)


class MultiDeligatorMethod(object):
    __slots__ = ("name", "parent")
    def __init__(self, parent, name):
        self.name = name
        self.parent = parent

    def __call__(self, *args, **kwargs):
        return_value = None
        for child in self.parent.children:
            method = getattr(child, self.name)
            return_value = apply(method, args, kwargs)
        return return_value

    def __str__(self):
        args = ", ".join((repr(arg) for arg in self.args))
        kwargs = ", ".join(("%s=%s" % (key, repr(value)) \
                 for key, value in self.kwargs.iteritems()))
        if args != "" and kwargs != "":
            argstring = "%s, %s" % (args, kwargs)
        elif args != "":
            argstring = args
        else:
            argstring = kwargs
        return "    %s(%s) = %r" % (self.name, argstring, self.result_value)


class MultiDeligator(object):
    def __init__(self, *target_objects):
        self.children = target_objects

    def __getattribute__(self, name):
        try:
            attr = super(MultiDeligator, self).__getattribute__(name)
            return attr
        except AttributeError:
            if name in ("__members__", "__methods__"):
                raise AttributeError()
            return MultiDeligatorMethod(self, name)


def create_spec_name(text):
    words = text.split("__")
    should_change = (len(words) != 2)
    for i, word in enumerate(words):
        if should_change:
           words[i] = word.replace("_", " ")
        should_change = not should_change
    return " ".join(words)

def create_method_repr(name, args, kwargs):
    if len(args) == 0:
        arg_str = ""
    elif len(args) == 1:
        arg_str = "%s" % str(args[0])
    else:
        arg_str = "*args=%s" % str(args)
    if len(kwargs) == 0:
        kwarg_str = ""
    else:
        kwarg_str = "*kwargs=%s" % str(kwargs)
    if arg_str != "" and kwarg_str != "":
        return "%s(%s, %s)" % (name, arg_str, kwarg_str)
    return "%s(%s%s)" % (name, arg_str, kwarg_str)
