from vanilla.dialogs import message


class ErrorMessage(object):

    def __init__(self, title, errors):
        self.title = title
        self.errors = errors

    def open(self):
        message(self.title, informativeText=self.messages)

    @property
    def messages(self):
        return ', '.join([error['message'] for error in self.errors])
