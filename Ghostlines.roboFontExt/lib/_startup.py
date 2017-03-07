from mojo.UI import AllFontWindows, CurrentFontWindow

from ghostlines.toolbar.manager import Manager
from ghostlines.toolbar.release_menu_item import ReleaseMenuItem
from ghostlines.toolbar.comments_menu_item import CommentsMenuItem

# Rather than use CurrentFontWindow, create this lambda which gets the last
# window in the array returned by AllFontWindows. CurrentFontWindow seems
# to have a bug where it does not return the window being opened during the
# 'fontWindowWillShowToolbarItems' callback. Until that is fixed, use this
# workaround...
newWindow = lambda: AllFontWindows()[-1]

fontToolbarEvent = "fontWindowWillShowToolbarItems"

Manager(newWindow, ReleaseMenuItem, index=-1).on(fontToolbarEvent)
Manager(newWindow, CommentsMenuItem, index=-1).on(fontToolbarEvent)
