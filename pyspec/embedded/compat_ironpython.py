# -*- coding ascii -*-

__pyspec = 1

import sys
import inspect

def get_source_code(depth=2):
    if sys.platform == "cli":
        return None
    return "".join(inspect.stack()[depth][4])


def get_source_code_with_file(depth=2):
    if sys.platform == "cli":
        return None
    frame = inspect.stack()[depth]
    return "".join(frame[4]), frame[1], frame[2]
