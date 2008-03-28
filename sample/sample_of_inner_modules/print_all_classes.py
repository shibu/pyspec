import pyspec.api
import pyspec.modulebrowser

class ModulePrinter(pyspec.api.ModuleAspect):
    def print_class(self):
        for class_obj in self.classes():
            class_obj.print_information()

class ClassPrinter(pyspec.api.ClassAspect):
    def print_information(self):
        print self.name()

# start - please type import sentences! But system modules will be ignored.

# end

browser = pyspec.modulebrowser.ModuleBrowser()
browser.add_listener("printer", ModulePrinter, ClassPrinter)
browser.load_all()
browser.send_all("printer", "print_class")
