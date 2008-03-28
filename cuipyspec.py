#!/usr/bin/env python

__pyspec = 1

import pyspec.textui

def main():
    runner = pyspec.textui.TextSpecTestRunner()
    runner.run()

if __name__ == '__main__':
    main()
