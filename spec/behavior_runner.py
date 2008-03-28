# -*- coding: ascii -*-

import behavior_pyspec
import behavior_pyspec_mockobject
import behavior_pyspec_util
import behavior_pyspec_outer_data
import behavior_pyspec_project
import behavior_pyspec_wxui_project
import behavior_pyunit_compatibility
import behavior_pyspec_dbc
import behavior_pyspec_legacy_support
import behavior_pyspec_localization

if __name__ == "__main__":
    import sys
    if "gui" in sys.argv or "-gui" in sys.argv:
        import pyspec.wxui.controller
        controller = pyspec.wxui.controller.WxPySpecController(0)
        controller.MainLoop()
    else:
        import pyspec
        pyspec.run_test()
