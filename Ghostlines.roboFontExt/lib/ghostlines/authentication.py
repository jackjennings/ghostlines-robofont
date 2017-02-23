from ghostlines.storage.app_storage import AppStorage
from ghostlines.windows.sign_in_window import SignInWindow
from ghostlines.windows.deferred_window import DeferredWindow


class Authentication(object):

    @staticmethod
    def require(cls):

        class AuthenticatedWindow(object):

            def __init__(self, *args, **kwargs):
                self.window = DeferredWindow(cls, *args, **kwargs)

            def open(self):
                token = AppStorage("accessToken").retrieve()
                # TODO: Retrieve returns NSNull if set to None. Empty string is
                # used to clear password for now, so check for None or ''
                if token != '' and token is not None:
                    self.window().open()
                else:
                    SignInWindow(success_window=self.window).open()

        return AuthenticatedWindow
