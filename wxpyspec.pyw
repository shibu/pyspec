#!/usr/bin/env python
# -*- coding: utf_8 -*-

__pyspec = 1

import pyspec.wxui.controller

def main():
    controller = pyspec.wxui.controller.WxPySpecController(0)
    controller.MainLoop()

if __name__ == '__main__':
    main()
