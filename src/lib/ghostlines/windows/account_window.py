from ghostlines.storage.app_storage import AppStorage
from ghostlines.windows.account_details_window import AccountDetailsWindow
from ghostlines.windows.sign_in_window import SignInWindow


class AccountWindow(object):

    def __init__(self, sign_in=SignInWindow, account_details=AccountDetailsWindow):
        if self.is_logged_in:
            self.window = account_details(logout_window=sign_in)
        else:
            self.window = sign_in(success_window=account_details)

    @property
    def is_logged_in(self):
        token = AppStorage("accessToken").retrieve()
        # TODO: Retrieve returns NSNull if set to None. Empty string is
        # used to clear password for now, so check for None or ''
        return token != '' and token is not None

    def open(self):
        self.window.open()
