from ghostlines.storage.lib_storage import LibStorage
from ghostlines.windows.legacy_release_window import LegacyReleaseWindow
from ghostlines.windows.release_window import ReleaseWindow
from ghostlines.windows.create_font_family_window import CreateFontFamilyWindow


class ReleaseMenuItem(object):

    def __init__(self, window):
        self.window = window
        self.font = window._font
        self.label = 'Ghostlines'
        self.identifier = 'ghostlinesUpload'

    def dispatch(self, *_):
        if self.has_legacy_data(self.font):
            LegacyReleaseWindow(self.font).open()
        elif self.has_family(self.font):
            ReleaseWindow(self.font, document=self.window.document).open()
        else:
            CreateFontFamilyWindow(self.font, success_window=ReleaseWindow).open()

    def has_legacy_data(self, font):
        legacy_storage = LibStorage(font.lib, "recipients")
        return legacy_storage.retrieve(default=None) is not None

    def has_family(self, font):
        family_id_storage = LibStorage(font.lib, "fontFamilyId")
        return family_id_storage.retrieve(default=None) is not None

    @property
    def icon(self):
        if self.has_legacy_data(self.font) or self.has_family(self.font):
            return 'upload.pdf'
        else:
            return 'create.pdf'
