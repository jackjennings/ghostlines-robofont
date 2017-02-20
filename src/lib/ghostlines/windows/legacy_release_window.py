import os
import tempfile
import requests

from vanilla import Window, List, Button, Sheet, EditText, TextBox, Group
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
from ghostlines.text import WhiteText

full_requirements_message = "Both a family name and a designer need to be set in order to provide enough information in the email to your testers."

# TODO: Detect this mapping in a more sustainable way
# or find out how to make filetype detection on the server more reliable
filetypes = {
    '.md': 'text/x-markdown',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain'
}


class LegacyReleaseWindow(BaseWindowController):

    def __init__(self, font):
        self.font = font
        self.recipients = FontRecipients(self.font)
        self.applicants = []
        self.note_draft_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.release_notes_draft')
        self.email_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.designer_email_address')
        self.license_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.license_filepath')

        self.window.background = Background((0, 0, -0, 235))
        self.window.attribution = AttributionText((15, 15, -15, 22), font)
        self.window.send_button = CounterButton((-215, 12, 200, 24),
                                                ("Send Release to All", "Send Release to {}"),
                                                callback=self.send)

        self.window.notes_field_label = TextBox((15, 52, -15, 22), WhiteText("Release Notes"))
        self.window.notes_field = NotesEditor((15, 75, -15, 80),
                                              draft_storage=self.note_draft_storage)

        self.window.email_address_field_label = TextBox((15, 170, 270, 22), WhiteText("Contact Email Included in Release"))
        self.window.email_address_field = EmailAddressField((15, 193, 270, 22),
                                                            storage=self.email_storage)

        self.window.license_field_label = TextBox((-285, 170, -15, 22), WhiteText("License"))
        self.window.license_field = FileUploadField((-285, 193, -15, 22),
                                                    storage=self.license_storage)

        self.window.recipients_label = TextBox((-285, 250, -15, 22), "Subscribers")
        self.window.recipients = List((-285, 273, 270, -49),
                                      self.recipients,
                                      selectionCallback=self.update_send_button)
        self.window.recipients.setSelection([])

        self.window.recipients_tip = TextBox((-200, -33, 185, 14),
                                             "cmd+click to select subset",
                                             alignment="right",
                                             sizeStyle="small")

        self.window.add_recipient_button = Button((-285, -39, 30, 24), "+", callback=self.add_recipient)
        self.window.remove_recipient_button = Button((-246, -39, 30, 24), "-", callback=self.remove_recipient)

        self.window.applicants = ApplicantList((15, 250, 270, 235), self.font, self.applicants, self.recipients, after_approve=self.add_approved_applicant)

        self.window.bind("became main", self.fetch_applicants)

        self.window.setDefaultButton(self.window.send_button)

    def fetch_applicants(self, sender):
        self.window.applicants.fetch()

    def add_approved_applicant(self, email):
        self.recipients.append(email)
        self.window.recipients.set(self.recipients)

    def open(self):
        if not self.font.info.familyName:
            message("Family Name must be set", full_requirements_message)
            return

        if not self.font.info.designer:
            message("Designer must be set", full_requirements_message)
            return

        self.window.open()

    def send(self, sender):
        recipients = self.window.recipients.get()
        selection = [recipients[i] for i in self.window.recipients.getSelection()]

        if selection == []:
            selection = self.window.recipients.get()

        recipients = ', '.join(selection)

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
                    recipients=recipients,
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
        for index in self.window.recipients.getSelection():
            del self.recipients[index]

        self.window.recipients.set(self.recipients)

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
            self.recipients.append(email)
            self.window.recipients.set(self.recipients)
            self.close_sheet()

    def update_send_button(self, sender):
        self.window.send_button.amount = len(self.window.recipients.getSelection())

    @property
    def title(self):
        return "Deliver {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((600, 500),
                      autosaveName=self.__class__.__name__,
                      title=self.title)
