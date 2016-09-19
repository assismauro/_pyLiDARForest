import os

class classLASTools(object):
    """Implement lastools processing features"""
    def __init__(self, inputfname, lastoolspath = r'c:\lastools\bin'):
        self.lastoolspath = lastoolspath
        self.inputfname = inputfname
        if not os.path.exists(inputfname):
            raise ValueError('File {0} doesn''t exists'.format(inputfname))



