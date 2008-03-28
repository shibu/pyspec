# -*- coding: ascii -*-

__pyspec = 1

import types
import pyspec.wxui.api as api

@api.entry_point
def init_module_dependency_plagin(addin_manager):
    return DependencyViewer(addin_manager)


@api.addin_menu_item("Module Dependency Map")
def show_dialog(dependency_viewer):
    dependency_viewer.show()


class DependencyViewer(object):
    def __init__(self, addin_manager):
        self.dialog = addin_manager.graphviz_dialog
        self.modules = addin_manager.get_module_observer()
        self.client_modules = None
        self.used_modules = None
        self.import_modules = {}
        self.pyspec_modules = None
        self.filter = None

    def show(self):
        self.dialog.set_title("Dependency Map")
        sources = []
        sources.append(self.create_dot_source(user_code=True))
        sources.append(self.create_dot_source(product_code=True))
        sources.append(self.create_dot_source(pyspec_only=True))
        self.dialog.set_source("All Modules", sources[0])
        self.dialog.set_source("Product Modules(w/o Test)", sources[1])
        self.dialog.set_source("With Pyspec", sources[2])
        self.dialog.show()

    def get_import_modules(self, module):
        import_modules = set()
        target = module.target()
        for name in dir(target):
            obj = getattr(target, name)
            #print "  ", name
            if type(obj) is types.ModuleType:
                import_modules.add(obj.__name__)
            if module.short_name().startswith("pyspec"):
                self.pyspec_modules.add(module.short_name())
        #print module.short_name(), import_modules
        return import_modules

    @staticmethod
    def is_pyspec(module):
        return hasattr(module.target(), "__pyspec")

    @classmethod
    def is_product_code(cls, module):
        return not cls.is_pyspec(module) and not module.is_spectest()

    def create_dot_source(self, pyspec_only=False, user_code=False, product_code=False):
        import StringIO
        out = StringIO.StringIO()

        print >>out, "digraph G {"
        print >>out, '  node [style="filled", shape="box", fontname="Helvetica", fontsize=11];'
        print >>out, '  graph [dpi=72];'

        self.categorize_modules(pyspec_only, user_code, product_code)
        self.write_dependency(out, product_code)

        print >>out, "}"
        return out.getvalue()

    def write_dependency(self, out, product_code):
        for module in self.modules.get_modules("pyspec"):
            name = module.short_name()
            if name in self.client_modules:
                self.dump_each_dependency(out, module, print_connection=True)
            elif name in self.used_modules:
                if module.is_spectest() and product_code:
                    continue
                self.dump_each_dependency(out, module, print_connection=False)

    def dump_each_dependency(self, out, module, print_connection=False):
        name = module.short_name()
        keyname = name.replace(".", "_")
        if self.is_pyspec:
            print >>out, '  %s [label="<PySpec>\\n%s", color="dodgerblue4", fillcolor="cornflowerblue"];' % (keyname, name)
        elif self.is_spectest():
            print >>out, '  %s [label="<Behavior>\\n%s", color="red", fillcolor="pink"];' % (keyname, name)
        else:
            print >>out, '  %s [label="%s", color="limegreen", fillcolor="palegreen"];' % (keyname, name)

        if print_connection:
            for depended_module in self.import_modules[name]:
                if depended_module not in self.filter:
                    print >>out, '  %s -> %s;' % (keyname, depended_module.replace(".", "_"))

    def categorize_modules(self, pyspec_only, user_code, product_code):
        self.client_modules = set()
        self.import_modules = {}
        self.used_modules = set()
        self.filter = set()
        self.pyspec_modules = set()

        for module in self.modules.get_modules("pyspec"):
            print module.short_name(), module.is_spectest()
            if product_code:
                if module.is_spectest():
                    self.filter.add(module.short_name())
            import_modules = self.get_import_modules(module)
            self.import_modules[module.short_name()] = import_modules

            if pyspec_only and self.is_pyspec(module):
                self.client_modules.add(module.short_name())
                for server in import_modules:
                    self.used_modules.add(server)
            elif user_code and not self.is_pyspec(module):
                self.client_modules.add(module.short_name())
                for server in import_modules:
                    self.used_modules.add(server)
            elif product_code and self.is_product_code(module):
                self.used_modules.add(module.short_name())
                for server in import_modules:
                    import_modules.add(server)
