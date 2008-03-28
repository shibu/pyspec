import sys, os
from distutils.sysconfig import get_python_lib

if sys.platform[:3] != "win":
    sys.exit()

try:
    prg = get_special_folder_path("CSIDL_COMMON_PROGRAMS")
except OSError:
    try:
        prg = get_special_folder_path("CSIDL_PROGRAMS")
    except OSError, reason:
        # give up - cannot install shortcuts
        print "cannot install shortcuts: %s" % reason
        sys.exit()


if __name__ == "__main__":
    if "-install" == sys.argv[1]:
        dest_dir = os.path.join(prg, "PySpec")
        try:
            os.mkdir(dest_dir)
            directory_created(dest_dir)
        except OSError:
            pass
        target = os.path.join(sys.prefix, "Scripts", "wxpyspec.pyw")
        path = os.path.join(dest_dir, "GUI SpecTester.lnk")
        create_shortcut(target, "GUI SpecTester", path)
        file_created(path)
        target = os.path.join(sys.prefix, "Removepyspec.exe")
        path = os.path.join(dest_dir, "Uninstall PySpec.lnk")
        arguments = "-u " + os.path.join(sys.prefix,
                                         "pyspec-wininst.log")

        create_shortcut(target, "Uninstall PySpec", path, arguments)
        file_created(path)

        print "See the shortcuts installed in the PySpec Programs Group"

    elif "-remove" == sys.argv[1]:
        pass

