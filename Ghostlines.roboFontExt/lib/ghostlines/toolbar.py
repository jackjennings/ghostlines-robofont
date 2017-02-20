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

    def __init__(self):
        addObserver(self, "addFontToolbar", "fontDidOpen")
        addObserver(self, "addFontToolbar", "newFontDidOpen")

    def addFontToolbar(self, info):
        window = CurrentFontWindow()
        font = CurrentFont()

        if window is None:
            return

        self.addToolbar(window,
                        'Ghostlines',
                        'ghostlinesUpload',
                        self.toolbar_icon_for_action(font),
                        self.openSender,
                        index=-2)

    def addToolbar(self, window, label, identifier, filename, callback, index=-1):
        toolbarItems = window.getToolbarItems()
        vanillaWindow = window.window()
        displayMode = vanillaWindow._window.toolbar().displayMode()
        imagePath = os.path.join(self.base_path, '..', 'ghostlines', 'resources', filename)
        image = NSImage.alloc().initByReferencingFile_(imagePath)

        newItem = dict(itemIdentifier = identifier,
            label = label,
            imageObject = image,
            callback = callback
        )

        toolbarItems.insert(index, newItem)
        vanillaWindow.addToolbar(toolbarIdentifier="toolbar-%s" % identifier,
                                 toolbarItems=toolbarItems,
                                 addStandardItems=False)
        vanillaWindow._window.toolbar().setDisplayMode_(displayMode)

    def openSender(self, sender):
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
