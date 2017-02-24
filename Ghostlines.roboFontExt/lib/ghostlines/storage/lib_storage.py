from ghostlines import env


class LibStorage(object):

    def __init__(self, lib, key):
        self.lib = lib
        self.key = "{}.{}".format(env.key_base, key)

    def store(self, content):
        if content is None:
            if self.key in self.lib:
                del self.lib[self.key]
        else:
            self.lib[self.key] = content

    def retrieve(self, default=''):
        if self.key in self.lib:
            return self.lib[self.key]
        else:
            return default
