'''
Created on Jul 25, 2013

@author: dtikhonov
'''
from general.templates.master_tpl import master_template
class fedora_tpl(master_template): # производим наш плагин от родительского класса
    name = 'fedora'
    tpl = """
    PROMPT 0
MENU TITLE Install currently supported Fedora releases
MENU LABEL ^Install currently supported Fedora releases

TEXT HELP
    Install currently supported Fedora releases
ENDTEXT


label uplvl
        MENU LABEL Back
        MENU EXIT

label spacer
        MENU LABEL
"""
    tpl_item = """      
    label %(label)s
        MENU LABEL %(label)s
        kernel %(pxeboot/vmlinuz)s
        initrd %(pxeboot/initrd.img)s
        APPEND repo=%(repo)s
            TEXT HELP
                 Selecting this will boot the
            ENDTEXT
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
        if '*Live-Desktop*' in params and not (params['*Live-Desktop*'] is None): 
            return menu + self.tpl_item_live % params
        else:
            params.update({'repo' : params['pxeboot/vmlinuz'].replace('images/pxeboot/vmlinuz', '')})
            return menu + self.tpl_item % params
    def install_patterns(self):
        return ['pxeboot/vmlinuz', 'pxeboot/initrd.img']
    def live_patterns(self):
        return ['*Live-Desktop*']
    def collect_patterns(self):
        return self.install_patterns() + self.live_patterns()