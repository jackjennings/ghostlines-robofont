import os

from AppKit import *
from vanilla import *

from mojo.UI import CurrentFontWindow
from mojo.events import addObserver
from mojo.roboFont import CurrentFont

from lib.UI.toolbarGlyphTools import ToolbarGlyphTools

from ghostlines.storage.lib_storage import LibStorage
from ghostlines.windows.ufo_delivery_window import UFODeliveryWindow
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

        family_id_storage = LibStorage(font.lib, "pm.ghostlines.ghostlines.fontFamilyId")

        if family_id_storage.retrieve(default=None) is not None:
            iconName = 'upload.pdf'
        else:
            iconName = 'create.pdf'

        self.addToolbar(window,
                        'Ghostlines',
                        'ghostlinesUpload',
                        iconName,
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
        family_id_storage = LibStorage(font.lib, "pm.ghostlines.ghostlines.fontFamilyId")

        if family_id_storage.retrieve(default=None) is not None:
            ReleaseWindow(font).open()
        else:
            CreateFontFamilyWindow(font, success_window=ReleaseWindow).open()
        # UFODeliveryWindow(CurrentFont()).open()
