from vanilla import Window, Button, EditText, TextBox

from ghostlines.lazy_property import lazy_property

class AccountWindow(BaseWindowController):

    def __init__(self):
        pass

    def open(self):
        self.window.open()

    @lazy_property
    def window(self):
        return Window((300, 300),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Account")
