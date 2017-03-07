from mojo.events import addObserver
from mojo.UI import AllFontWindows

from ghostlines.toolbar.toolbar import Toolbar


class Manager(object):

    def __init__(self, window_getter, item_class, index=-1):
        self.window_getter = window_getter
        self.item_class = item_class
        self.index = index

    def on(self, *events):
        for event in events:
            addObserver(self, "add_font_toolbar", event)

    def add_font_toolbar(self, info):
        window = self.window_getter()
        item = self.item_class(window)

        toolbar = Toolbar(info['toolbarItems'])
        toolbar.add(item, index=self.index)
