import os
import tempfile
import requests

from vanilla import Window, List, Button, Sheet, EditText, TextBox, Group, VerticalLine
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.windows.progressWindow import ProgressWindow

from ghostlines.lazy_property import lazy_property
from ghostlines.api import Ghostlines
from ghostlines.font_recipients import FontRecipients
from ghostlines.background import Background
from ghostlines.applicant_list import ApplicantList
from ghostlines.attribution_text import AttributionText
from ghostlines.fields.notes_editor import NotesEditor
from ghostlines.fields.email_address_field import EmailAddressField
from ghostlines.fields.file_upload_field import FileUploadField
from ghostlines.ui.counter_button import CounterButton
from ghostlines.storage.lib_storage import LibStorage

full_requirements_message = "Both a family name and a designer need to be set in order to provide enough information in the email to your testers."

# TODO: Detect this mapping in a more sustainable way
# or find out how to make filetype detection on the server more reliable
filetypes = {
    '.md': 'text/x-markdown',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain'
}


class ReleaseWindow(BaseWindowController):

    def __init__(self, font):
        self.font = font
        self.subscribers = FontRecipients(self.font)
        self.applicants = []
        self.note_draft_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.release_notes_draft')
        self.email_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.designer_email_address')
        self.license_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.license_filepath')
        
        self.window.subscribers_label = TextBox((15, 15, 270, 22), "Subscribers", sizeStyle="small")
        self.window.subscribers = List((15, 37, 270, 205),
                                      self.subscribers,
                                      selectionCallback=self.update_send_button)
        self.window.subscribers.setSelection([])

        self.window.subscribers_tip = TextBox((15, 253, 270, 14),
                                             "cmd+click to select subset",
                                             alignment="right",
                                             sizeStyle="small")

        self.window.add_recipient_button = Button((15, 248, 30, 24), "+", callback=self.add_recipient)
        self.window.remove_recipient_button = Button((55, 248, 30, 24), "-", callback=self.remove_recipient)

        self.window.applicants = ApplicantList((15, 295, 270, 200), self.font, self.applicants, self.subscribers, after_approve=self.add_approved_applicant)
        
        self.window.vertical_line = VerticalLine((300, 0, 1, -0))

        self.window.release_info = Group((315, 15, -15, -15))

        self.window.release_info.font_name_label = TextBox((0, 0, -0, 22), "Font Name", sizeStyle="small")
        self.window.release_info.font_name = TextBox((0, 19, -0, 22), (font.info.familyName or ""))
        self.window.release_info.font_author_label = TextBox((0, 60, -0, 22), "Designer", sizeStyle="small")
        self.window.release_info.font_author = TextBox((0, 79, -0, 22), (font.info.designer or ""))
        self.window.release_info.version_label = TextBox((0, 120, -0, 22), "Version Number", sizeStyle="small")
        
        if font.info.versionMajor is not None and font.info.versionMinor is not None:
            font_version = "{}.{}".format(font.info.versionMajor, font.info.versionMinor)
        else:
            font_version = u"\u2014"
        
        self.window.release_info.version = TextBox((0, 139, -0, 22), font_version)

        self.window.release_info.notes_field_label = TextBox((0, 176, -0, 22), "Release Notes", sizeStyle="small")
        self.window.release_info.notes_field = NotesEditor((0, 198, -0, 175), draft_storage=self.note_draft_storage)

        self.window.release_info.license_field_label = TextBox((0, 393, -0, 22), "Attach License", sizeStyle="small")
        self.window.release_info.license_field = FileUploadField((0, 410, -0, 22), storage=self.license_storage)

        self.window.release_info.send_button = CounterButton((0, -24, -0, 24),
                                                        ("Send Release to All", "Send Release to {}"),
                                                        callback=self.send)

        self.window.bind("became main", self.fetch_applicants)

    def fetch_applicants(self, sender):
        self.window.applicants.fetch()

    def add_approved_applicant(self, email):
        self.subscribers.append(email)
        self.window.subscribers.set(self.subscribers)

    def open(self):
        if not self.font.info.familyName:
            message("Family Name must be set", full_requirements_message)
            return

        if not self.font.info.designer:
            message("Designer must be set", full_requirements_message)
            return

        self.window.open()

    def send(self, sender):
        subscribers = self.window.subscribers.get()
        selection = [subscribers[i] for i in self.window.subscribers.getSelection()]

        if selection == []:
            selection = self.window.subscribers.get()

        subscribers = ', '.join(selection)

        progress = ProgressWindow('', tickCount=3, parentWindow=self.window)

        try:
            tmpdir = tempfile.mkdtemp(prefix="ghostlines")

            progress.update('Generating OTF')

            # Should be controlled which options are used somewhere
            filename = os.path.join(tmpdir, self.font.info.familyName + '.otf')

            self.font.generate(filename, "otf", decompose=True, checkOutlines=True, autohint=True)

            progress.update('Sending via Ghostlines')

            with open(filename, 'rb') as otf:
                params = dict(
                    otf=otf,
                    recipients=subscribers,
                    notes=self.window.notes_field.get(),
                    designer_email_address=self.window.email_address_field.get()
                )

                license_path = self.license_storage.retrieve()

                if license_path is not '' and os.path.exists(license_path):
                    with open(license_path, 'rb') as license:
                        filename = os.path.basename(license_path)
                        _, extension = os.path.splitext(license_path)
                        content_type = filetypes[extension]
                        params['license'] = (filename, license, content_type)
                        response = Ghostlines('v0.1').send(**params)
                else:
                    response = Ghostlines('v0.1').send(**params)

            if response.status_code == requests.codes.created:
                message("{} was delivered".format(self.font.info.familyName))
            else:
                print repr(response)
                message("{} could not be delivered".format(self.font.info.familyName),
                        "Error code: {}\n{}".format(response.status_code, response.json()))
        finally:
            progress.close()

    def remove_recipient(self, sender):
        for index in self.window.subscribers.getSelection():
            del self.subscribers[index]

        self.window.subscribers.set(self.subscribers)

    def add_recipient(self, sender):
        self.window.sheet = Sheet((250, 89), self.window)
        self.window.sheet.recipient = EditText((15, 15, -15, 22), "", placeholder="Email Address")
        self.window.sheet.cancel_button = Button((-190, 52, 80, 22),
                                                 'Cancel',
                                                 callback=self.close_sheet)
        self.window.sheet.create_button = Button((-95, 52, 80, 22),
                                                 'Add',
                                                 callback=self.create_recipient)
        self.window.sheet.setDefaultButton(self.window.sheet.create_button)
        self.window.sheet.open()

    def close_sheet(self, *args):
        self.window.sheet.close()

    def create_recipient(self, *args):
        email = self.window.sheet.recipient.get()

        if not email is '':
            self.subscribers.append(email)
            self.window.subscribers.set(self.subscribers)
            self.close_sheet()

    def update_send_button(self, sender):
        pass
        # self.window.send_button.amount = len(self.window.subscribers.getSelection())

    @property
    def title(self):
        return "Ghostlines: Release {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((600, 510),
                      autosaveName=self.__class__.__name__,
                      title=self.title)

if __name__ == "__main__":
    ReleaseWindow(CurrentFont()).open()
