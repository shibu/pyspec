# -*- coding: ascii -*-

__pyspec = 1

import os
import sys
import imp
import pyspec.addin


class CUIAddinLoader(pyspec.addin.AddinLoaderBase):
    def __init__(self):
        super(CUIAddinLoader, self).__init__(addin_folder_name="cuiaddin")


class CUIAddinManager(pyspec.addin.AddinManagerBase):
    def load_addin(self):
        super(CUIAddinManager, self).load_addin(CUIAddinLoader())
