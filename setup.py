# -*- coding ascii -*-

import os
from distutils.core import setup
from distutils.command.install_data import install_data
import pyspec, pyspec.embedded

# todo: migration with doctest
# todo: complete class browser
# todo: implement plugin browser
# todo: fix reload system(wxui)
# todo: fix update_recent_file()


if pyspec.__version__ != pyspec.embedded.__version__:
    raise ValueError("pyspec version and pyspec.embedded are different!")


class smart_install_data(install_data):
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)


def search_packages(path, result=[]):
    if os.path.exists(os.path.join(path, "__init__.py")):
        result.append(path)
    for filename in os.listdir(path):
        child_path = os.path.join(path, filename)
        if os.path.isdir(child_path):
            search_packages(child_path, result)
    return result


def find_data_files(path, result=[], prefix=None, ok_exts=[], ng_exts=[]):
    files = []
    for filename in os.listdir(path):
        if filename == ".svn":
            continue
        child_path = os.path.join(path, filename)
        is_ok = False
        if os.path.isdir(child_path):
            find_data_files(child_path, result, prefix, ok_exts, ng_exts)
        elif os.path.isfile(child_path):
            is_ng = False
            for extfilter in ng_exts:
                if child_path.endswith(extfilter):
                    is_ng = True
                    break
            if is_ng:
                break
            if not ok_exts:
                is_ok = True
            for extfilter in ok_exts:
                if child_path.endswith(extfilter):
                    is_ok = True
                    break
        if is_ok:
            files.append(child_path)
    if files:
        if prefix is not None:
            result.append((os.path.join(prefix, path), files))
        else:
            result.append((path, files))
    return result


data_files = []
find_data_files('resource', data_files,
                prefix='pyspec', ok_exts=['.png', '.xrc'])
find_data_files('doc', data_files,
                prefix='pyspec', ok_exts=['.html'])
find_data_files('spec', data_files,
                prefix='pyspec', ok_exts=['.py'])
find_data_files(os.path.join('pyspec','wxaddin'), data_files,
                ng_exts=['.py', '.pyo', '.pyc', '.db'])
find_data_files(os.path.join('pyspec','cuiaddin'), data_files,
                ng_exts=['.py', '.pyo', '.pyc', '.db'])


setup(name = 'pyspec',
      version = pyspec.__version__,
      url = 'http://www.codeplex.com/pyspec',
      author = 'Shibukawa Yoshiki',
      author_email = ('yoshiki at shibu.jp / '
                      'Yoshiki_Shibukawa at n.t.rd.honda.co.jp'),
      packages = search_packages("pyspec"),
      scripts = ['wxpyspec.pyw', 'wxpyspec.py',
                 'cuipyspec.py', 'pyspec_postinstall.py'],
      cmdclass = {'install_data': smart_install_data},
      data_files=data_files
)

# python setup.py sdist -f
# python setup.py bdist_wininst --install-script=pyspec_postinstall.py
# python setup.py bdist_rpm
