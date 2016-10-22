class LibStorage(object):

    def __init__(self, lib, key):
        self.lib = lib
        self.key = key

    def store(self, content):
        self.lib[self.key] = content

    def retrieve(self):
        if self.lib.has_key(self.key):
            return self.lib[self.key]
        else:
            return ''
