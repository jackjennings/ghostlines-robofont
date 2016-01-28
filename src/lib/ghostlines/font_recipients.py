class FontRecipients(object):

    KEY = 'pm.ghostlines.ghostlines.recipients'

    def __init__(self, font):
        self.font = font

    def __iter__(self):
        return iter(self.font.lib.get(self.KEY, []))

    def __delitem__(self, key):
        del self.font.lib.get(self.KEY, [])[key]

    def append(self, email):
        if not self.font.lib.has_key(self.KEY):
            self.font.lib[self.KEY] = []

        self.font.lib.get(self.KEY).append(email)
