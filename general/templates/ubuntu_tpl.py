'''
Created on Jul 25, 2013

@author: dtikhonov
'''
from general.templates.master_tpl import master_template
class ubuntu_tpl(master_template): # производим наш плагин от родительского класса
    name = 'ubuntu'
    tpl = """
    PROMPT 0
MENU TITLE Install currently supported UBUNTU releases
MENU LABEL ^Install currently supported UBUNTU releases

TEXT HELP
    Install currently supported UBUNTU releases
ENDTEXT


label uplvl
        MENU LABEL Back
        MENU EXIT

label spacer
        MENU LABEL
"""
    tpl_item = """      
label %(label)s
        kernel %(ubuntu-installer/*/linux)s
        initrd=%(ubuntu-installer/*/initrd.gz)s
        ramdisk_size=16432
    """
    tpl_item_live = """
    label %(label)s
    MENU DEFAULT
    MENU LABEL %(label)s (memdisk)
    TEXT HELP
        Being tested
    ENDTEXT
    kernel memdisk
    append iso initrd=%(*Live-Desktop*)s
    IPAPPEND 3
    """
    def gen_menu(self, menu, params):
        return  menu + self.tpl_item % params
    def install_patterns_rsync(self):
        return ['ubuntu-installer/*/linux', 'ubuntu-installer/*/initrd.gz']
    def collect_patterns(self):
        return self.install_patterns_rsync()