import requests
import webbrowser

from vanilla import Window, Button, EditText, TextBox
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

from ghostlines import env
from ghostlines.lazy_property import lazy_property
from ghostlines.error_message import ErrorMessage
from ghostlines.storage.app_storage import AppStorage


class SignInWindow(BaseWindowController):

    def __init__(self, success_window):
        self.success_window = success_window
        self.window.introduction = TextBox((15, 15, -15, 22), 'Sign in with your Ghostlines account.', sizeStyle='small')
        self.window.email_label = TextBox((15, 44, -15, 22), 'Email:', sizeStyle='small')
        self.window.email_field = EditText((15, 61, -15, 22))
        self.window.password_label = TextBox((15, 101, -15, 22), 'Password:', sizeStyle='small')
        self.window.password_field = EditText((15, 119, -15, 22))
        self.window.need_account_button = Button((15, -35, 110, 17), 'Need Account?', callback=self.make_account, sizeStyle="small")
        self.window.sign_in_button = Button((175, -38, 110, 22), 'Sign In', callback=self.sign_in)
        self.window.setDefaultButton(self.window.sign_in_button)

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
            AppStorage('accessToken').store(token)
            self.success_window(self.__class__, account=account).open()
            self.window.close()
        else:
            ErrorMessage('Sign In Error', json['errors']).open()

    def make_account(self, _):
        webbrowser.open('https://ghostlines.pm/signup/')

    @lazy_property
    def window(self):
        return Window((300, 196),
                      autosaveName=self.__class__.__name__,
                      title="Ghostlines: Sign In")
