from mojo.extensions import getExtensionDefault, setExtensionDefault

from ghostlines import env


class AppStorage(object):

    def __init__(self, key):
        self.key = "{}.{}".format(env.key_base, key)

    def store(self, value):
        return setExtensionDefault(self.key, value)

    def retrieve(self):
        return getExtensionDefault(self.key)
