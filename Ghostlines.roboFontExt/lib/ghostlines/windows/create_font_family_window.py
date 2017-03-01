import requests

from vanilla import Window, Button, TextBox, EditText
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines import env
from ghostlines.api import Ghostlines
from ghostlines.authentication import Authentication
from ghostlines.lazy_property import lazy_property
from ghostlines.error_message import ErrorMessage
from ghostlines.windows.sign_in_window import SignInWindow
from ghostlines.storage.app_storage import AppStorage
from ghostlines.storage.lib_storage import LibStorage


@Authentication.require
class CreateFontFamilyWindow(BaseWindowController):

    def __init__(self, font, success_window):
        self.font = font
        self.success_window = success_window

        self.window.family_name_label = TextBox((15, 15, -15, 22), 'Family Name', sizeStyle='small')
        self.window.family_name = EditText((15, 40, -15, 22), font.info.familyName)

        self.window.designer_name_label = TextBox((15, 81, -15, 22), 'Designer', sizeStyle='small')
        self.window.designer_name = EditText((15, 106, -15, 22), font.info.openTypeNameDesigner)

        self.window.create_button = Button((175, -38, 110, 22), 'Add Font', callback=self.create)

    def open(self):
        self.window.open()

    def create(self, _):
        token = AppStorage('accessToken').retrieve()
        api = Ghostlines("v1", token=token)
        name = self.window.family_name.get()
        designer_name = self.window.designer_name.get()
        response = api.create_font_family(name, designer_name)
        json = response.json()
        if response.status_code == 201:
            family_id_storage = LibStorage(self.font.lib, "fontFamilyId")
            family_id_storage.store(json["id"])

            if self.font.info.openTypeNameDesigner is None:
                self.font.info.openTypeNameDesigner = designer_name

            if self.font.info.familyName is None:
                self.font.info.familyName = name

            self.success_window(self.font).open()
            self.window.close()
        else:
            ErrorMessage('Could not create a font family', json['errors']).open()

    @lazy_property
    def window(self):
        return Window((300, 200),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Add Font")
