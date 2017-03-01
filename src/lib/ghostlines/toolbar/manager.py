from mojo.UI import CurrentFontWindow
from mojo.events import addObserver
from mojo.roboFont import CurrentFont

from ghostlines.toolbar.toolbar import Toolbar


class Manager(object):

    def __init__(self, item_class, index=-1):
        self.item_class = item_class
        self.index = index

    def on(self, *events):
        for event in events:
            addObserver(self, "add_font_toolbar", event)

    def add_font_toolbar(self, info):
        menu_item = self.item_class(CurrentFont())

        toobar = Toolbar(CurrentFontWindow())
        toobar.add(menu_item, index=self.index)
