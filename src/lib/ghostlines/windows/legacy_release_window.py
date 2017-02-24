import os
import tempfile
import requests

from vanilla import Window, List, Button, Sheet, EditText, TextBox, Group
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.windows.progressWindow import ProgressWindow

from ghostlines.api import Ghostlines
from ghostlines.authentication import Authentication
from ghostlines.lazy_property import lazy_property
from ghostlines.font_recipients import FontRecipients
from ghostlines.background import Background
from ghostlines.legacy.applicant_list import ApplicantList
from ghostlines.attribution_text import AttributionText
from ghostlines.fields.notes_editor import NotesEditor
from ghostlines.fields.email_address_field import EmailAddressField
from ghostlines.fields.file_upload_field import FileUploadField
from ghostlines.ui.counter_button import CounterButton
from ghostlines.storage.lib_storage import LibStorage
from ghostlines.storage.app_storage import AppStorage
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
        self.note_draft_storage = LibStorage(self.font.lib, "release_notes_draft")
        self.email_storage = LibStorage(self.font.lib, "designer_email_address")
        self.license_storage = LibStorage(self.font.lib, "license_filepath")

        self.window.banner_background = Background((0, -40, 0, 40), 1)
        self.window.upgrade_tip = TextBox((15, -30, -15, 22),
                                          WhiteText("Ghostlines is out of Beta. If you have an account, upgrade:"))
        self.window.upgrade_button = Button((-205, -31, 185, 22),
                                            "Migrate from Beta",
                                            callback=self.migrate,
                                            sizeStyle="small")

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
        self.window.recipients = List((-285, 273, 270, -89),
                                      self.recipients,
                                      selectionCallback=self.update_send_button)
        self.window.recipients.setSelection([])

        self.window.recipients_tip = TextBox((-200, -73, 185, 14),
                                             "cmd+click to select subset",
                                             alignment="right",
                                             sizeStyle="small")

        self.window.add_recipient_button = Button((-285, -79, 30, 24), "+", callback=self.add_recipient)
        self.window.remove_recipient_button = Button((-246, -79, 30, 24), "-", callback=self.remove_recipient)

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

    def migrate(self, sender):
        MigrationAssistant(self.font).open()
        self.window.close()

    @property
    def title(self):
        return "Deliver {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((600, 540),
                      autosaveName=self.__class__.__name__,
                      title=self.title)


@Authentication.require
class MigrationAssistant(object):

    def __init__(self, font):
        self.font = font
        self.recipients = FontRecipients(self.font)

        if 'pm.ghostlines.ghostlines.registry_token' in self.font.lib:
            self.roster_token = self.font.lib['pm.ghostlines.ghostlines.registry_token']
        else:
            self.roster_token = None

        self.window.content = Group((15, 15, -15, -15))
        self.window.content.font_name_label = TextBox((0, 0, -0, 22), "Font Name", sizeStyle="small")
        self.window.content.font_name = TextBox((0, 19, -0, 22), self.font.info.familyName)
        self.window.content.font_author_label = TextBox((0, 55, -0, 22), "Designer", sizeStyle="small")
        self.window.content.font_author = TextBox((0, 74, -0, 22), self.font.info.designer)

        self.window.content.recipients_label = TextBox((0, 114, -15, 22), "Subscribers", sizeStyle="small")
        self.window.content.recipients = List((0, 135, -0, 190), self.recipients, drawFocusRing=False, allowsEmptySelection=True)
        self.window.content.recipients.setSelection([])

        self.window.content.roster_label = TextBox((0, 350, -15, 22), "Application Page", sizeStyle="small")
        self.window.content.roster_status = TextBox((0, 370, -15, 22), self.roster_status)

        self.window.content.confirmation_button = Button((0, -24, 0, 24), "Complete Migration", callback=self.migrate)

        self.window.content.explainer = TextBox((0, 405, -15, 66),
                                                "A new font entry will be created on Ghostlines with the details above. Any pending applicants will be retained if you have activated that feature.",
                                                sizeStyle="small")

        self.window.setDefaultButton(self.window.content.confirmation_button)

    def open(self):
        self.window.open()

    def migrate(self, *_):
        token = AppStorage("accessToken").retrieve()
        api = Ghostlines("v1", token=token)
        response = api.migrate(list(self.recipients), self.font.info.familyName, self.font.info.designer, self.roster_token)
        json = response.json()

        if response.status_code == 201:
            LibStorage(self.font.lib, "fontFamilyId").store(json["id"])

            expired_keys = [
                'pm.ghostlines.ghostlines.registry_token',
                'pm.ghostlines.ghostlines.recipients',
                'pm.ghostlines.ghostlines.designer_email_address'
            ]

            for key in expired_keys:
                if key in self.font.lib:
                    del self.font.lib[key]

            old_note_storage = LibStorage(self.font.lib, "release_notes_draft")
            old_license_storage = LibStorage(self.font.lib, "license_filepath")
            LibStorage(self.font.lib, "releaseNotesDraft").store(old_note_storage.retrieve(default=None))
            LibStorage(self.font.lib, "licenseFilepath").store(old_license_storage.retrieve(default=None))
            old_note_storage.store(None)
            old_license_storage.store(None)

            from ghostlines.windows.release_window import ReleaseWindow

            self.window.close()
            ReleaseWindow(self.font).open()
        else:
            ErrorMessage("Oops", json["errors"])

    @property
    def roster_status(self):
        if self.roster_token is not None:
            return "Enabled"
        else:
            return u"\u2014"

    @property
    def title(self):
        return "Ghostlines: Migrate from Beta".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((320, 520),
                      autosaveName=self.__class__.__name__,
                      title=self.title)
