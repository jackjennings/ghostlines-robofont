import os

from AppKit import NSImage


class Toolbar(object):

    base_path = os.path.dirname(__file__)
    resource_path = os.path.join(base_path, '..', '..', 'ghostlines', 'resources')

    def __init__(self, doodle_window):
        self.window = doodle_window.window()

    def add(self, item, index=None):
        if self.window is None:
            return

        image_path = os.path.join(self.resource_path, item.icon)
        image = NSImage.alloc().initByReferencingFile_(image_path)

        new_item = dict(
            itemIdentifier = item.identifier,
            label = item.label,
            callback = item.dispatch,
            imageObject = image
        )

        self.window.addToolbarItem(new_item, index=index)
