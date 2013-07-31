'''
Created on Jul 25, 2013

@author: dtikhonov
'''
import os
import inspect
from general.templates.master_tpl import master_template
class Collector(object):
    Plugins = []
    plugin_dir = "templates"
    url = ""


    def __init__(self):
        self.LoadPlugins()

    def LoadPlugins(self):
        for fname in os.listdir(self.plugin_dir):
            if fname.endswith (".py"):
                module_name = fname[:-3]
                if "master_tpl" not in module_name and module_name != "__init__":
                    package_obj = __import__(self.plugin_dir + "." + module_name)
                    module_obj = getattr (package_obj, module_name)
                    for elem in dir (module_obj):  
                        obj = getattr (module_obj, elem)
                        if elem is not "master_template":
                            if inspect.isclass (obj):
                                if issubclass (obj, master_template):
                                    print ("Load module %s" % module_name)
                                    a = obj()
                                    self.Plugins.append (a)
        return  
