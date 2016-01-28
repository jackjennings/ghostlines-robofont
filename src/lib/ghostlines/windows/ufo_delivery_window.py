from vanilla import Window, List
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines.lazy_property import lazy_property

full_requirements_message = "Both a family name and a designer need to be set in order to provide enough information in the email to your testers."

class UFODeliveryWindow(BaseWindowController):

    def __init__(self, font):
        self.font = font

        columns = [{"title": "Email Address",
                    "key": "email_address",
                    "editable": True}]
        items = [{"email_address": "foo@bar.com"}]

        self.window.recipients = List((10, 10, -10, -10), items, columnDescriptions=columns)

    def open(self):
        if not self.font.info.familyName:
            message("Family Name must be set", full_requirements_message)
            return

        if not self.font.info.designer:
            message("Designer must be set", full_requirements_message)
            return

        self.window.open()

    @property
    def title(self):
        return "Deliver {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((300, 300),
                      autosaveName=self.__class__.__name__,
                      title=self.title)
