import requests
import webbrowser

from vanilla import Window, Button, EditText, TextBox
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines import env
from ghostlines.lazy_property import lazy_property
from ghostlines.storage.app_storage import AppStorage


class SignInWindow(BaseWindowController):

    def __init__(self, success_window):
        self.success_window = success_window
        self.window.introduction = TextBox((15, 15, -15, 44), "Sign in using credentials from ghostlines.pm.")
        self.window.email_label = TextBox((15, 70, -15, 22), "Account Email:")
        self.window.email_field = EditText((15, 100, -15, 22))
        self.window.password_label = TextBox((15, 140, -15, 22), "Account Password:")
        self.window.password_field = EditText((15, 165, -15, 22))
        self.window.sign_in_button = Button((15, 205, 125, 22), "Sign In", callback=self.sign_in)
        self.window.need_account_button = Button((160, 205, 125, 22), "Need Account?", callback=self.make_account)

    def open(self):
        self.window.open()

    def sign_in(self, _):
        email_address = self.window.email_field.get()
        password = self.window.password_field.get()
        data = {'email_address': email_address, 'password': password}
        response = requests.post('{}/v1/authenticate'.format(env.api_url), data=data)
        json = response.json()
        if response.status_code == 201: # Success!
            account = json['account']
            token = json['token']
            AppStorage('pm.ghostlines.ghostlines.access_token').store(token)
            self.success_window(self.__class__, account=account).open()
            self.window.close()
        else:
            self.display_error_message(json['errors'])

    def make_account(self, _):
        webbrowser.open('https://ghostlines.pm/signup')

    def display_error_message(self, errors):
        messages = ', '.join([error['message'] for error in errors])
        message('Sign In Error', informativeText=messages)

    @lazy_property
    def window(self):
        return Window((300, 350),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Account")
