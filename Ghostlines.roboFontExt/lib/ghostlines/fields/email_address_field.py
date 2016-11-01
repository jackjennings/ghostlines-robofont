from vanilla import EditText

from ghostlines.storage.null_storage import NullStorage


class EmailAddressField(EditText):

    def __init__(self, dimensions, storage=NullStorage()):
        self.storage = storage

        super(EmailAddressField, self).__init__(dimensions, callback=self.store)

        self.set(self.storage.retrieve())

    def store(self, sender):
        self.storage.store(sender.get())
