from mojo.UI import CurrentFontWindow

from ghostlines.toolbar.manager import Manager
from ghostlines.toolbar.release_menu_item import ReleaseMenuItem
from ghostlines.toolbar.comments_menu_item import CommentsMenuItem


fontToolbarEvent = "fontWindowWillShowToolbarItems"

Manager(CurrentFontWindow, ReleaseMenuItem, index=-1).on(fontToolbarEvent)
Manager(CurrentFontWindow, CommentsMenuItem, index=-1).on(fontToolbarEvent)
