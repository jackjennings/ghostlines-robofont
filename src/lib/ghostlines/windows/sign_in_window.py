import requests
import webbrowser

from vanilla import Window, Button, EditText, TextBox
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines.lazy_property import lazy_property
from ghostlines.storage.app_storage import AppStorage


class SignInWindow(BaseWindowController):

    def __init__(self, success_window):
        self.success_window = success_window
        self.window.introduction = TextBox((15, 15, -15, 22), 'Sign in with your Ghostlines account.', sizeStyle='small')
        self.window.email_label = TextBox((15, 44, -15, 22), 'Email:', sizeStyle='small')
        self.window.email_field = EditText((15, 61, -15, 22))
        self.window.password_label = TextBox((15, 101, -15, 22), 'Password:', sizeStyle='small')
        self.window.password_field = EditText((15, 119, -15, 22))
        self.window.need_account_button = Button((15, -38, 110, 22), 'Need Account?', callback=self.make_account)
        self.window.sign_in_button = Button((175, -38, 110, 22), 'Sign In', callback=self.sign_in)
        self.window.setDefaultButton(self.window.sign_in_button)

    def open(self):
        self.window.open()

    def sign_in(self, _):
        email_address = self.window.email_field.get()
        password = self.window.password_field.get()
        response = requests.post('https://ghostlines-staging.herokuapp.com/v1/authenticate', data={'email_address': email_address, 'password': password})
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
        return Window((300, 196),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Sign In")
