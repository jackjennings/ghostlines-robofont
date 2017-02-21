import requests

from vanilla import Window, Button, TextBox
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines import env
from ghostlines.lazy_property import lazy_property
from ghostlines.storage.app_storage import AppStorage


class AccountDetailsWindow(BaseWindowController):

    def __init__(self, logout_window, account=None):
        self.logout_window = logout_window
        if account is not None:
            self.account = account
        self.window.email_label = TextBox((15, 15, -15, 22), 'Account Email:', sizeStyle='small')
        self.window.account_email = TextBox((15, 40, -15, 22), self.account['email_address'], alignment='center')
        self.window.sign_out_button = Button((175, -38, 110, 22), 'Sign Out', callback=self.sign_out)

    def open(self):
        self.window.open()

    def sign_out(self, _):
        AppStorage("pm.ghostlines.ghostlines.accessToken").store('')
        self.logout_window(self.__class__).open()
        self.window.close()

    @lazy_property
    def account(self):
        token = AppStorage('pm.ghostlines.ghostlines.accessToken').retrieve()
        request = requests.get('{}/v1/account'.format(env.api_url), headers={'Authorization': 'Bearer {}'.format(token)})
        return request.json()

    @lazy_property
    def window(self):
        return Window((300, 110),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Account Details")
