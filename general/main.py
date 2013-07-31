'''
Created on Jul 1, 2013

@author: dtikhonov
'''
import subprocess
from general.template.template import Collector
import urllib.request
import re
import ftplib
import copy
import os, errno
main_menu_tpl = """
DEFAULT vesamenu.c32 
TIMEOUT 600
ONTIMEOUT BootLocal
PROMPT 0
MENU INCLUDE pxelinux.cfg/pxe.conf
NOESCAPE 1
LABEL BootLocal
        localboot 0
        TEXT HELP
        Boot to local hard disk
        ENDTEXT
"""

submenu_tpl = """
    PROMPT 0
MENU TITLE This is submenu of %s
MENU LABEL ^This is submenu of %s

label uplvl
        MENU LABEL Back
        MENU EXIT

label spacer
        MENU LABEL
"""


def get_main_dir_list(url):
    main_dir = []
    if meth_pref(url) == 'rsync':
        cmdline = ["rsync", "--temp-dir=/tmp", url]
        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        for entry in proc.stdout:
            try:
                items = entry.strip().split(None, 2)
                #print (url + '/' + items[0].decode("utf-8"))
                if "MOTD" not in items[0].decode("utf-8") and "mirrors" not in items[0].decode("utf-8"):
                    main_dir.append(items[0].decode("utf-8"))
            except IndexError:
                pass
    return main_dir
responses_ok = {
    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),
    }
def exists(url, path):
    if url.startswith('rsync://'):
        url_resource = url.split('rsync://')[1]
        try:
            response = urllib.request.urlopen('http://'+url_resource + '/' + path)
            code = response.getcode()
            if responses_ok[code]:
                #print("http is avaible")
                #print('http://'+url_resource + '/' + path)
                return 'http://'+url_resource + '/' + path
        except urllib.error.HTTPError:
            print("http is not available; try ftp")
            remote = ftplib.FTP(url_resource)
            remote.login()
            try:
                remote.cwd(path)
                #print("ftp avaible")
                #print("ftp://" + url_resource + '/' + path)
                return "ftp://" + url_resource + '/' + path
            except ftplib.error_perm:
                print("sorry, resourcse is not available")
                return False


def meth_pref(url):
    if url.startswith('rsync:'):
        return 'rsync'
    if url.startswith('http:'):
        return 'http'
    return 'ftp'

def get_cmd(template, url):
        cmdline = []
        exclude_dir = []
        include_dir = []
        if meth_pref(url) == 'rsync':
            exclude_dir = ['--exclude=' + i for i in template.exclude_dir]
            include_dir.append('--exclude=*')
            include_dir = ['--include=' + i for i in template.collect_patterns()]
            include_dir.append('--include=*/')
            url = url
            cmdline = ["rsync", "--temp-dir=/tmp", "-r", "--prune-empty-dirs"]
            for i in include_dir:
                cmdline.append(i)
            for i in exclude_dir:
                cmdline.append(i)
            cmdline.append(url)
        return cmdline  

def gen_main_menu(main_menu_tpl,menu_item):
    return main_menu_tpl + """
    MENU BEGIN %s
    MENU TITLE %s 
        LABEL Previous
        MENU LABEL Previous Menu
        TEXT HELP
        Return to previous menu
        ENDTEXT
        MENU EXIT
        MENU SEPARATOR
        MENU INCLUDE %s/%s.menu
    MENU END
    """ % (menu_item, menu_item, menu_item, menu_item)  
def walk_dict(result, submenu_list):
    if len(result.keys()) >= 2:
        for key in result.keys():
            if key not in submenu_list:
                submenu_list.append(key + '/')
        return
    else:
        for key in result.keys():
                walk_dict(result[key], submenu_list)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        

def directory_walker_rsync(url, main_dir, master_template):
    not_empty_main_dirs = []
    global main_menu_tpl
    main_menu = main_menu_tpl
    for directory in main_dir:
        submenu             = []
        for plugin in master_template.Plugins:
                p = copy.deepcopy(plugin)
                items_find = {}
                result = {}
                print(get_cmd(p, url + '/' + directory))
                proc = subprocess.Popen(get_cmd(p, url + '/' + directory), stdout=subprocess.PIPE)
                for entry in proc.stdout:
                    try:
                        items = entry.strip().split(None, 4)
                        # проверяем, что это не сообщение сервера или папка mirrors
                        if "MOTD" not in items[0].decode("utf-8") and "mirrors" not in items[0].decode("utf-8"):
                            menu_item = directory + '/' +  items[4].decode("utf-8")
                            hierarchy = menu_item.split('/')
                            # если это не сама директория
                            if len(hierarchy)>1:
                                # заменяем паттерны в шаблонах на regex выражения (возможно требуется доработка
                                for pattern in p.collect_patterns():
                                    pattern_regex = re.sub('[*]', '(.*)', pattern)
                                    #pattern_regex = pattern
                                    m = re.search(pattern_regex, menu_item)
                                    # если по regex шаблону нашли в выведенной строке что-то, то идем дальше
                                    if m:
                                        path = exists(url, menu_item)
                                        # проверяем доступен ли ресурс по http или ftp
                                        if path: 
                                            menu_enty = [x for x in re.split(pattern_regex, menu_item) if x][0]
                                            if menu_enty not in submenu:
                                                items_find[menu_enty] = {}
                                                submenu.append(menu_enty)
                                            items_find[menu_enty].update({pattern : path}) 
                                            
                                            local_result = result
                                            for node in hierarchy:
                                                local_result = local_result.setdefault(node, {})
                                            #print(result)
                                            if directory not in not_empty_main_dirs:
                                                not_empty_main_dirs.append(directory)
                                                main_menu = gen_main_menu(main_menu,directory)
                                                mkdir_p(directory)
                    except IndexError:
                        pass 
                if(items_find):
                    submenu_tree = []
                    walk_dict(result,submenu_tree)
                    submenu = main_menu_tpl
                    for submenu_item in submenu_tree:
                        submenu = gen_main_menu(submenu,submenu_item[:-1])
                        mkdir_p(directory + '/' + submenu_item[:-1])
                        item_menu = main_menu_tpl
                        for label, item in items_find.items():
                            if submenu_item in label:                   
                                item.update({'label' : label})
                                item_menu = p.gen_menu(item_menu, item)
                        f = open(directory + '/' + submenu_item[:-1]+'/'+submenu_item[:-1]+'.menu','w')
                        f.write(item_menu)
                        f.close()
                    f = open(directory + '/' + directory +'.menu','w')
                    f.write(submenu)
                    f.close()
    print("main menu is: ")
    f = open('main.menu','w')
    f.write(main_menu)
    f.close()
    print(main_menu)

if __name__ == "__main__":
    url = 'rsync://mirrors.kernel.org' #just example
    main_dir = get_main_dir_list(url)
    print(main_dir)
    master_template = Collector()
    directory_walker_rsync(url, main_dir, master_template)