from mojo.extensions import getExtensionDefault, setExtensionDefault


class AppStorage(object):

    def __init__(self, key):
        self.key = key

    def store(self, value):
        return setExtensionDefault(self.key, value)

    def retrieve(self):
        return getExtensionDefault(self.key)
