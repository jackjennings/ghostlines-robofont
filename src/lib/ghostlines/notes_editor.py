from vanilla import TextEditor


class NullStorage(object):

    def store(self, *args):
        print args

    def retrieve(self):
        return ''


class NotesEditor(TextEditor):

    def __init__(self, dimensions, draft_storage=NullStorage()):
        self.draft_storage = draft_storage

        super(NotesEditor, self).__init__(dimensions, callback=self.store_draft)

        self.set(self.draft_storage.retrieve())

    def store_draft(self, sender):
        self.draft_storage.store(sender.get())
