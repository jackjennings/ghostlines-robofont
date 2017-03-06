import os

from AppKit import NSImage


class Toolbar(object):

    base_path = os.path.dirname(__file__)
    resource_path = os.path.join(base_path, '..', '..', 'ghostlines', 'resources')

    def __init__(self, items):
        self.items = items

    def add(self, item, index=None):
        image_path = os.path.join(self.resource_path, item.icon)
        image = NSImage.alloc().initByReferencingFile_(image_path)

        new_item = dict(
            itemIdentifier = item.identifier,
            label = item.label,
            callback = item.dispatch,
            imageObject = image
        )

        self.items.insert(index, new_item)
