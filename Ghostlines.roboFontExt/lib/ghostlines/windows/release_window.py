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
from ghostlines.error_message import ErrorMessage
from ghostlines.fields.notes_editor import NotesEditor
from ghostlines.fields.email_address_field import EmailAddressField
from ghostlines.fields.file_upload_field import FileUploadField
from ghostlines.ui.counter_button import CounterButton
from ghostlines.storage.lib_storage import LibStorage
from ghostlines.storage.app_storage import AppStorage


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

        self.subscribers = self.font_family["subscribers"]
        self.applicants = []
        self.note_draft_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.release_notes_draft')
        self.email_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.designer_email_address')
        self.license_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.license_filepath')

        self.window.background = Background((-299, -52, 299, 52))

        self.window.release_info = Group((315, 15, -15, -15))

        self.window.release_info.font_name_label = TextBox((0, 0, -0, 22), "Font Name", sizeStyle="small")
        self.window.release_info.font_name = TextBox((0, 19, -0, 22), self.font_family["name"])
        self.window.release_info.font_author_label = TextBox((0, 60, -0, 22), "Designer", sizeStyle="small")
        self.window.release_info.font_author = TextBox((0, 79, -0, 22), self.font_family["designer_name"])
        self.window.release_info.version_label = TextBox((0, 120, -0, 22), "Version Number", sizeStyle="small")

        self.window.release_info.version = TextBox((0, 139, -0, 22), self.font_version)

        self.window.release_info.notes_field_label = TextBox((0, 176, -0, 22), "Release Notes", sizeStyle="small")
        self.window.release_info.notes_field = NotesEditor((0, 198, -0, 175), draft_storage=self.note_draft_storage)

        self.window.release_info.license_field_label = TextBox((0, 393, -0, 22), "Attach License", sizeStyle="small")
        self.window.release_info.license_field = FileUploadField((0, 410, -0, 22), storage=self.license_storage)

        self.window.release_info.send_button = CounterButton((0, -24, -0, 24),
                                                        ("Send Release to All", "Send Release to {}"),
                                                        callback=self.send)

        self.window.vertical_line = VerticalLine((300, 0, 1, -0))

        self.window.subscribers_label = TextBox((15, 15, 270, 22), "Subscribers", sizeStyle="small")
        self.window.subscribers = List((15, 37, 270, 205),
                                       self.subscribers,
                                       columnDescriptions=[
                                           {
                                               "title": "Name",
                                               "key": "name",
                                               "editable": False
                                           }, {
                                               "title": "Email Address",
                                               "key": "email_address",
                                               "editable": False
                                           }
                                       ],
                                       selectionCallback=self.update_send_button)
        self.window.subscribers.setSelection([])

        self.window.subscribers_tip = TextBox((15, 253, 270, 14),
                                             "cmd+click to select subset",
                                             alignment="right",
                                             sizeStyle="small")

        self.window.show_subscriber_sheet_button = Button((15, 248, 30, 24), "+", callback=self.show_subscriber_sheet)
        self.window.remove_subscriber_button = Button((55, 248, 30, 24), "-", callback=self.remove_subscriber)

        self.window.applicants = ApplicantList((15, 295, 270, 200), self.font, self.applicants, self.subscribers, after_approve=self.add_approved_applicant)

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

    def show_subscriber_sheet(self, sender):
        self.window.sheet = Sheet((250, 107), self.window)
        self.window.sheet.name = EditText((15, 15, -15, 22), "", placeholder="Name")
        self.window.sheet.email_address = EditText((15, 43, -15, 22), "", placeholder="Email Address")
        self.window.sheet.cancel_button = Button((-190, 70, 80, 22),
                                                 'Cancel',
                                                 callback=self.close_sheet)
        self.window.sheet.create_button = Button((-95, 70, 80, 22),
                                                 'Add',
                                                 callback=self.create_subscriber)
        self.window.sheet.setDefaultButton(self.window.sheet.create_button)
        self.window.sheet.open()

    def create_subscriber(self, *args):
        name = self.window.sheet.name.get()
        email_address = self.window.sheet.email_address.get()
        family_id_storage = LibStorage(self.font.lib, "pm.ghostlines.ghostlines.fontFamilyId")
        token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
        api = Ghostlines("v1", token=token)
        response = api.create_subscriber(family_id_storage.retrieve(), name, email_address)
        json = response.json()

        if response.status_code == 201:
            font_family = api.font_family(family_id_storage.retrieve()).json()
            self.window.subscribers.set(font_family["subscribers"])
            self.close_sheet()
        else:
            ErrorMessage("Couldn't create that subscriber", json["errors"])

    def remove_subscriber(self, sender):
        family_id_storage = LibStorage(self.font.lib, "pm.ghostlines.ghostlines.fontFamilyId")
        token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
        api = Ghostlines("v1", token=token)

        for index in self.window.subscribers.getSelection():
            subscriber = self.window.subscribers[index]
            api.delete_subscriber(subscriber["id"])
            font_family = api.font_family(family_id_storage.retrieve()).json()
            self.window.subscribers.set(font_family["subscribers"])

    def close_sheet(self, *args):
        self.window.sheet.close()

    def update_send_button(self, sender):
        self.window.release_info.send_button.amount = len(self.window.subscribers.getSelection())

    @property
    def font_version(self):
        major = self.font.info.versionMajor
        minor = self.font.info.versionMinor
        if major is not None and minor is not None:
            return "{}.{}".format(major, minor)
        else:
            return u"\u2014"

    @property
    def title(self):
        return "Ghostlines: Release {}".format(self.font.info.familyName)

    @lazy_property
    def window(self):
        return Window((600, 510),
                      autosaveName=self.__class__.__name__,
                      title=self.title)

    @lazy_property
    def font_family(self):
        family_id_storage = LibStorage(self.font.lib, "pm.ghostlines.ghostlines.fontFamilyId")
        token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
        return Ghostlines("v1", token=token).font_family(family_id_storage.retrieve()).json()
