# -*- coding ascii -*-

__pyspec = 1


import sys


STDOUT = 0
STDERR = 1
CONTEXT_INFO = 2
DATA_PROVIDER_INFO = 3
REPORT_OUT = 4

if sys.platform == "cli":
    import System
    import System.IO

    class DotNetStdOutTransfer(System.IO.TextWriter):
        def __init__(self):
            super(DotNetStdOutTransfer, self).__init__()
            self.system_console = System.Console.Out

        def Write(self, output):
            sys.stdout.write(str(output))

        def WriteLine(self, output):
            sys.stdout.write("%s\n", str(output))

        def reset(self):
            System.Console.SetOut(self.system_console)


    class DotNetStdErrTransfer(System.IO.TextWriter):
        def __init__(self):
            super(DotNetStdErrTransfer, self).__init__()
            self.system_console = System.Console.Error

        def Write(self, output):
            sys.stderr.write(str(output))

        def WriteLine(self, output):
            sys.stderr.write("%s\n", str(output))

        def reset(self):
            System.Console.SetError(self.system_console)


class ConsoleHook(object):
    """This class is used for gathering console out.
    """
    def __init__(self, receiver, console_id, write_through = False):
        self.receiver = receiver
        self.console_id = console_id
        self.write_through = write_through
        self.dotnet_console = None
        self.system_console = None
        if console_id == STDOUT:
            self.system_console = sys.stdout
            if sys.platform == "cli":
                self.dotnet_console = DotNetStdOutTransfer()
            sys.stdout = self
        elif console_id == STDERR:
            self.system_console = sys.stderr
            if sys.platform == "cli":
                self.dotnet_console = DotNetStdErrTransfer()
            sys.stderr = self
        else:
            self.system_console = None

    def write(self, s):
        if not s:
            return
        if self.console_id < 2 and not isinstance(s, basestring):
            s = str(s)
        self.receiver.console_out(self.console_id, s)
        if self.write_through and self.system_console is not None:
            self.system_console.write(s)

    def writelines(self, iterable):
        for line in iterable:
            self.write(line)

    def reset_system_console(self):
        if self.console_id == STDOUT:
            sys.stdout = self.system_console
        elif self.console_id == STDERR:
            sys.stderr = self.system_console
        if self.dotnet_console is not None:
            self.dotnet_console.reset()


def get_console_encoder(output_encoding):
    import codecs
    if sys.platform == "cli":
        return sys.stdout
    else:
        writer = codecs.getwriter(output_encoding)
        return writer(sys.stdout)


def format_exception_only(etype, value):
    """This function is special version for IronPython
    """
    import types
    import traceback

    if (isinstance(etype, types.InstanceType) or
        etype is None or isinstance(etype, basestring)):
        return [traceback._format_final_exc_line(etype, value)]

    stype = etype.__name__

    if not issubclass(etype, SyntaxError):
        return [traceback._format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    try:
        msg, (filename, lineno, offset, badline) = value
    except Exception:
        pass
    else:
        filename = filename or "<string>"
        lines.append('  File "%s", line %d\n' % (filename, lineno))
        if badline is not None:
            lines.append('    %s\n' % badline.strip())
            if offset is not None:
                caretspace = badline[:offset].lstrip()
                caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                lines.append('   %s^\n' % ''.join(caretspace))
            value = msg

    lines.append(traceback._format_final_exc_line(stype, value))
    return lines


_original_format_exception_only = None


def dummy_function(param):
    pass


def patch_for_iron_python():
    import sys
    import traceback
    if sys.platform == "cli":
        _original_format_exception_only = traceback.format_exception_only
        traceback.format_exception_only = format_exception_only
        sys.setprofile = dummy_function
        sys.settrace = dummy_function
