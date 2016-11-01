class NullStorage(object):

    def store(self, *args):
        print args

    def retrieve(self):
        return ''
