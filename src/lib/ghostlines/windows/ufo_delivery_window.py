import os
import tempfile

from vanilla import Window, List, Button
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines.lazy_property import lazy_property
from ghostlines.api import Ghostlines

full_requirements_message = "Both a family name and a designer need to be set in order to provide enough information in the email to your testers."

class UFODeliveryWindow(BaseWindowController):

    def __init__(self, font):
        self.font = font

        items = ["foo@bar.com"]

        self.window.recipients = List((15, 15, -15, -49), items)
        self.window.send_button = Button((-135, -39, 120, 24), "Deliver", callback=self.send)

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

    @property
    def title(self):
        return "Deliver {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((300, 300),
                      autosaveName=self.__class__.__name__,
                      title=self.title)
