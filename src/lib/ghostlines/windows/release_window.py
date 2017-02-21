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

        self.note_draft_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.release_notes_draft')
        self.email_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.designer_email_address')
        self.license_storage = LibStorage(self.font.lib, 'pm.ghostlines.ghostlines.license_filepath')
        self.family_id_storage = LibStorage(self.font.lib, "pm.ghostlines.ghostlines.fontFamilyId")

        self.subscribers = self.font_family["subscribers"]
        self.applicants = []

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

        self.window.applicants = \
            ApplicantList((15, 295, 270, 200),
                          self.font_family["applicant_roster"],
                          self.family_id_storage.retrieve(),
                          after_approve=self.refresh_subscribers)

        self.window.bind("became main", self.fetch_applicants)

    def fetch_applicants(self, sender):
        self.window.applicants.fetch()

    def refresh_subscribers(self, *args):
        token = AppStorage("pm.ghostlines.ghostlines.accessToken").retrieve()
        api = Ghostlines("v1", token=token)
        font_family = api.font_family(self.family_id_storage.retrieve()).json()
        self.window.subscribers.set(font_family["subscribers"])

    def open(self):
        if not self.font.info.familyName:
            message("Family Name must be set", full_requirements_message)
            return

        if not self.font.info.designer:
            message("Designer must be set", full_requirements_message)
            return

        self.window.open()

    def send(self, *_):
        subscribers = self.window.subscribers.get()
        subscriber_ids = [subscribers[i]["id"] for i in self.window.subscribers.getSelection()]
        notes = self.note_draft_storage.retrieve()
        font_family_id = self.family_id_storage.retrieve()
        license_path = self.license_storage.retrieve()

        progress = ProgressWindow('', tickCount=3, parentWindow=self.window)

        try:
            tmpdir = tempfile.mkdtemp(prefix="ghostlines")

            progress.update('Generating OTF')

            # Should be controlled which options are used somewhere
            otf_path = os.path.join(tmpdir, '{}.otf'.format(self.font.info.familyName))
            self.font.generate(otf_path, "otf", decompose=True, checkOutlines=True, autohint=True)

            progress.update('Sending via Ghostlines')

            params = dict(
                notes=notes,
                font_family_id=font_family_id
            )

            with open(otf_path, 'rb') as otf:
                params['otfs'] = [(os.path.basename(otf_path), otf.read(), "application/octet-stream")]

            if subscriber_ids:
                params['subscriber_ids'] = subscriber_ids

            if self.license_exists:
                with open(license_path, 'rb') as license:
                    filename = os.path.basename(license_path)
                    _, extension = os.path.splitext(license_path)
                    content_type = filetypes[extension]
                    params['license'] = (filename, license.read(), content_type)

            token = AppStorage("pm.ghostlines.ghostlines.accessToken").retrieve()
            response = Ghostlines('v1', token=token).create_release(**params)

            if response.status_code == requests.codes.created:
                message("{} was delivered".format(self.font.info.familyName))
            else:
                ErrorMessage("{} could not be delivered".format(self.font.info.familyName),
                             response.json()["errors"])
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
        token = AppStorage("pm.ghostlines.ghostlines.accessToken").retrieve()
        api = Ghostlines("v1", token=token)
        response = api.create_subscriber(self.family_id_storage.retrieve(), name, email_address)
        json = response.json()

        if response.status_code == 201:
            self.refresh_subscribers()
        else:
            ErrorMessage("Couldn't create that subscriber", json["errors"])

    def remove_subscriber(self, sender):
        token = AppStorage("pm.ghostlines.ghostlines.accessToken").retrieve()
        api = Ghostlines("v1", token=token)

        for index in self.window.subscribers.getSelection():
            subscriber = self.window.subscribers[index]
            api.delete_subscriber(subscriber["id"])

        self.refresh_subscribers()

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

    @property
    def license_exists(self):
        filepath = self.license_storage.retrieve()
        return filepath is not '' and os.path.exists(filepath)

    @lazy_property
    def window(self):
        return Window((600, 510),
                      autosaveName=self.__class__.__name__,
                      title=self.title)

    @lazy_property
    def font_family(self):
        token = AppStorage("pm.ghostlines.ghostlines.accessToken").retrieve()
        return Ghostlines("v1", token=token).font_family(self.family_id_storage.retrieve()).json()
