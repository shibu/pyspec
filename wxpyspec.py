#!/usr/bin/env python
# -*- coding: ascii -*-

__pyspec = 1

def main():
    import pyspec.wxui.controller
    controller = pyspec.wxui.controller.WxPySpecController(0)
    controller.MainLoop()

if __name__ == '__main__':
    main()
