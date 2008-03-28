# -*- coding: ascii -*-

"""Idea of event binder decoretor is Mr.NoboNobo's and TurboGears. Thanks.
   Mr.NoboNobo's site: http://python.matrix.jp
"""

__pyspec = 1

__all__ = ('expose',
           'bind_event_handler',
           'get_resource_path',
           'load_png')

import pyspec.util

attr_key = "__pyspec_wxutil_eventhandler"

class binder_class(object):
    def __init__(self, event, id):
        self.event = event
        self.id = id

    def __call__(self, method):
        from pyspec.util import Struct
        event_info = Struct(event=self.event, id=self.id)
        if hasattr(method, attr_key):
            getattr(method, attr_key).append(event_info)
        else:
            setattr(method, attr_key, [event_info])
        return method


def expose(event, id=None):
    return binder_class(event, id)


def bind_event_handler(frame, controller=None):
    import wx
    from wx.xrc import XRCID
    if controller is None:
        controller = frame
    for name in dir(controller):
        obj = getattr(controller, name)
        if hasattr(obj, attr_key):
            for event_info in getattr(obj, attr_key):
                if event_info.id is None:
                    frame.Bind(event_info.event, obj)
                else:
                    frame.Bind(event_info.event, obj, id=XRCID(event_info.id))



def get_resource_path(filename):
    import os
    if os.path.exists("resource"):
        return os.path.join("resource", filename)
    path_in_lib = pyspec.util.pyspec_file_path("resource", filename)
    if os.path.exists(path_in_lib):
        return path_in_lib
    return os.path.abspath(os.path.join(path_in_lib, "..", "..", "..", "resource", filename))


def load_png(filename):
    import wx
    return wx.Image(filename, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
