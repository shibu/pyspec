# -*- coding: ascii -*-

"""PySpec extension api.
   This module enable following extension features:
     - Add aspect to modules, classes, methods
     - Add Add-in
"""


__pyspec = 1


import os
import sys
from pyspec.api import (ModuleAspect, ClassAspect, MethodAspect,
                        EventHandlerRegister)


def entry_point(method):
    """Notify the target method is special function of pyspec extension.
    Method name must be in folloing list:
      add_trace() : not implement yet
      add_profile() : not implement yet
    """
    if "pyspec.addin" in sys.modules:
        addin = sys.modules["pyspec.addin"]
        addin.AddinLoaderBase.add_entry_point(method)


def event_handler(event_type):
    if event_type not in ("init_optparse", "read_option", "on_run_test",
                          "on_finish_test"):
        ValueError("Invalid event type: %s" % event_type)
    return EventHandlerRegister(event_type)

