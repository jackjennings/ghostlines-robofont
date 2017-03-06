from vanilla import Popover
from vanilla.dialogs import message

from ghostlines import env
from ghostlines.webview import WebView
from ghostlines.storage.lib_storage import LibStorage
from ghostlines.storage.app_storage import AppStorage


class CommentsMenuItem(object):

    def __init__(self, font, window):
        self.window = window
        self.font = font
        self.label = 'Feedback'
        self.identifier = 'ghostlinesFeedback'
        self.icon = 'feedback.pdf'
        self.enabled = False

        self.font_family_id_storage = LibStorage(self.font.lib, "fontFamilyId")

        self.popover = Popover((300, 400), parentView=self.content_view)
        self.popover.web = WebView((0, 0, -0, -0))

        # Binding to "should close" instead of "close", as the event doesn't
        # seem to fire...
        self.window.window().bind("should close", self.clear_webview)

    def dispatch(self, sender):
        token = AppStorage("accessToken").retrieve()
        font_family_id = self.font_family_id_storage.retrieve(default=None)

        if font_family_id is not None and token is not None and token is not '':
            window = self.window.window().getNSWindow()
            mouseDown = window.mouseLocationOutsideOfEventStream()
            height = self.content_view.frame().size.height
            rect = (mouseDown.x, height - 1, 1, 1)
            headers = {'Authorization': 'Bearer {}'.format(token)}

            self.popover.open(preferredEdge="top", relativeRect=rect)

            if not self.popover.web.url:
                comment_ui_url ="{}/ui/font_families/{}/comments".format(env.api_url, font_family_id)
                self.popover.web.load(comment_ui_url, headers)
        else:
            message("You must register a font first", "Click on the Ghostlines menu item to create a record for this font on Ghostlines. You will then be able to view the comments from all of your releases by clicking this icon.")

    def clear_webview(self, *_):
        if self.popover.web.url:
            self.popover.web.unload()

        return True

    @property
    def content_view(self):
        return self.window.window().getNSWindow().contentView()
