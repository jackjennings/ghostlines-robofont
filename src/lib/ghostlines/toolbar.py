import os

from AppKit import *
from vanilla import *

from mojo.UI import CurrentFontWindow
from mojo.events import addObserver
from mojo.roboFont import CurrentFont

from lib.UI.toolbarGlyphTools import ToolbarGlyphTools

from ghostlines.storage.lib_storage import LibStorage
from ghostlines.windows.legacy_release_window import LegacyReleaseWindow
from ghostlines.windows.release_window import ReleaseWindow
from ghostlines.windows.create_font_family_window import CreateFontFamilyWindow

class GhostlinesToolbar(object):

    base_path = os.path.dirname(__file__)

    def __init__(self, *events):
        for event in events:
            addObserver(self, "add_font_toolbar", event)

    def add_font_toolbar(self, info):
        window = CurrentFontWindow()
        font = CurrentFont()

        if window is None:
            return

        self.add_toolbar(window,
                         'Ghostlines',
                         'ghostlinesUpload',
                         self.toolbar_icon_for_action(font),
                         self.open_sender,
                         index=-2)

    def add_toolbar(self, window, label, identifier, filename, callback, index=-1):
        toolbar_items = window.getToolbarItems()
        vanilla_window = window.window()
        display_mode = vanilla_window._window.toolbar().displayMode()
        image_path = os.path.join(self.base_path, '..', 'ghostlines', 'resources', filename)
        image = NSImage.alloc().initByReferencingFile_(image_path)

        newItem = dict(itemIdentifier = identifier,
            label = label,
            imageObject = image,
            callback = callback
        )

        toolbar_items.insert(index, newItem)
        vanilla_window.addToolbar(toolbarIdentifier="toolbar-%s" % identifier,
                                 toolbarItems=toolbar_items,
                                 addStandardItems=False)
        vanilla_window._window.toolbar().setDisplayMode_(display_mode)

    def open_sender(self, sender):
        font = CurrentFont()

        if self.has_legacy_data(font):
            LegacyReleaseWindow(font).open()
        elif self.has_family(font):
            ReleaseWindow(font).open()
        else:
            CreateFontFamilyWindow(font, success_window=ReleaseWindow).open()

    def has_legacy_data(self, font):
        legacy_storage = LibStorage(font.lib, "pm.ghostlines.ghostlines.recipients")
        return legacy_storage.retrieve(default=None) is not None

    def has_family(self, font):
        family_id_storage = LibStorage(font.lib, "pm.ghostlines.ghostlines.fontFamilyId")
        return family_id_storage.retrieve(default=None) is not None

    def toolbar_icon_for_action(self, font):
        if self.has_legacy_data(font) or self.has_family(font):
            return 'upload.pdf'
        else:
            return 'create.pdf'
