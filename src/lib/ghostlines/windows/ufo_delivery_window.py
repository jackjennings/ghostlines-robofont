import os
import tempfile

from vanilla import Window, List, Button, Sheet, EditText
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines.lazy_property import lazy_property
from ghostlines.api import Ghostlines
from ghostlines.font_recipients import FontRecipients

full_requirements_message = "Both a family name and a designer need to be set in order to provide enough information in the email to your testers."

class UFODeliveryWindow(BaseWindowController):

    def __init__(self, font):
        self.font = font
        self.items = FontRecipients(self.font)

        self.window.recipients = List((15, 15, -15, -49), self.items)
        self.window.send_button = Button((-135, -39, 120, 24), "Deliver", callback=self.send)

        self.window.add_recipient_button = Button((15, -39, 30, 24), "+", callback=self.add_recipient)
        self.window.remove_recipient_button = Button((50, -39, 30, 24), "-", callback=self.remove_recipient)

        self.window.setDefaultButton(self.window.send_button)

    def open(self):
        if not self.font.info.familyName:
            message("Family Name must be set", full_requirements_message)
            return

        if not self.font.info.designer:
            message("Designer must be set", full_requirements_message)
            return

        self.window.open()

    def send(self, sender):
        recipients = ', '.join(self.window.recipients.get())

        tmpdir = tempfile.mkdtemp(prefix="ghostlines")

        # Should be controlled which options are used somewhere
        filename = os.path.join(tmpdir, self.font.info.familyName + '.otf')

        self.font.generate(filename, "otf", decompose=True, checkOutlines=True, autohint=True)

        with open(filename, 'rb') as otf:
            Ghostlines('v0.1').send(otf=otf, recipients=recipients)

    def remove_recipient(self, sender):
        for index in self.window.recipients.getSelection():
            del self.items[index]

        self.window.recipients.set(self.items)

    def add_recipient(self, sender):
        self.window.sheet = Sheet((250, 89), self.window)
        self.window.sheet.recipient = EditText((15, 15, -15, 22), '')
        self.window.sheet.cancel_button = Button((-215, 52, 100, 22),
                                                 'Cancel',
                                                 callback=self.close_sheet)
        self.window.sheet.create_button = Button((-115, 52, 100, 22),
                                                 'Add',
                                                 callback=self.create_recipient)
        self.window.sheet.setDefaultButton(self.window.sheet.create_button)
        self.window.sheet.open()

    def close_sheet(self, *args):
        self.window.sheet.close()

    def create_recipient(self, *args):
        email = self.window.sheet.recipient.get()

        if not email is '':
            self.items.append(email)
            self.window.recipients.set(self.items)
            self.close_sheet()

    @property
    def title(self):
        return "Deliver {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((300, 300),
                      autosaveName=self.__class__.__name__,
                      title=self.title)
