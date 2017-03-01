import os

from AppKit import NSImage

from mojo.UI import CurrentFontWindow
from mojo.events import addObserver
from mojo.roboFont import CurrentFont


class Manager(object):

    base_path = os.path.dirname(__file__)
    resource_path = os.path.join(base_path, '..', '..', 'ghostlines', 'resources')

    def __init__(self, menu_class):
        self.menu_class = menu_class

    def on(self, *events):
        for event in events:
            addObserver(self, "add_font_toolbar", event)

    def add_font_toolbar(self, info):
        window = CurrentFontWindow()
        font = CurrentFont()
        menu_item = self.menu_class(font)

        if window is None:
            return

        self.add_toolbar(window,
                         menu_item.label,
                         menu_item.identifier,
                         menu_item.icon,
                         menu_item.dispatch,
                         index=-2)

    def add_toolbar(self, window, label, identifier, filename, callback, index=-1):
        toolbar_items = window.getToolbarItems()
        vanilla_window = window.window()
        display_mode = vanilla_window._window.toolbar().displayMode()
        image_path = os.path.join(self.resource_path, filename)
        image = NSImage.alloc().initByReferencingFile_(image_path)

        newItem = dict(
            itemIdentifier = identifier,
            label = label,
            imageObject = image,
            callback = callback
        )

        toolbar_items.insert(index, newItem)
        vanilla_window.addToolbar(toolbarIdentifier="toolbar-%s" % identifier,
                                  toolbarItems=toolbar_items,
                                  addStandardItems=False)
        vanilla_window._window.toolbar().setDisplayMode_(display_mode)
