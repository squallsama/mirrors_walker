class master_template(object):
    name = ""
    main_folder = ""
    exclude_dir = ['*']
    arch        = []
    def __init__(self):
        return
    '''
    def get_cmd(self,url):
        if self.meth_pref(url) == 'rsync':
            self.exlude_dir = ['--exclude=' + i for i in self.exlude_dir]
            self.include_dir = ['--include=' + i for i in self.collect_patterns()]
            self.include_dir.append('--include=*/')
            self.url = url
            self.cmdline = ["rsync", "--temp-dir=/tmp", "-r", "--prune-empty-dirs"]
            for i in self.include_dir:
                self.cmdline.append(i)
            for i in self.exlude_dir:
                self.cmdline.append(i)
            self.cmdline.append(url)
        return self.cmdline
    def meth_pref(self, url):
        if url.startswith('rsync:'):
            return 'rsync'
        if url.startswith('http:'):
            return 'http'
        return 'ftp'
    '''
    def collect_patterns(self):
        return
    def gen_menu(self, menu, params):
        pass
