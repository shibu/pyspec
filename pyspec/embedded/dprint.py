# -*- coding ascii -*-

import os
import re
import sys
import string
import compat_ironpython

__pyspec = 1

_default_output_file = sys.stderr
_run_in_pyspec = False
_variable_name_splitter = re.compile(r"dprint\((.*)\)")


def dprint(*variables, **kwargs):
    """printf debug support function.

    options:
        file - output file(default=sys.stderr)
        sep - seperator(default=', ')
        end - string that added at the end of strings(default='\n')
        varsep - seperator between variable name and value(default='=')
        fileinfo - show filename and line number(deafult=True)
    """
    output_file = kwargs.get("file", _default_output_file)
    seperator = kwargs.get("sep", ", ")
    end = kwargs.get("end", "\n")
    varsep = kwargs.get("varsep", "=")
    sourceline, filepath, line = compat_ironpython.get_source_code_with_file()
    filename = os.path.split(filepath)[1].replace(".pyc", ".py")
    filename = filename.replace(".pyo", ".py")
    if kwargs.get("fileinfo", True):
        fileinfo = string.Template("$filename($line):").substitute(
                       filename=filename, line=line)
    else:
        fileinfo = ""
    match = _variable_name_splitter.search(sourceline)
    result_template = string.Template("@$fileinfo$result$end")
    if match:
        results = []
        variable_names = match.group(1).split(",")
        variable_tamplate = string.Template("$var$varsep$value")
        for i, value in enumerate(variables):
            results.append(variable_tamplate.substitute(
                           var=variable_names[i].strip(), value=value,
                           varsep=varsep))
    else:
        results = [str(value) for value in variables]
    output_file.write(result_template.substitute(
                         fileinfo=fileinfo, result=seperator.join(results),
                         end=end))
