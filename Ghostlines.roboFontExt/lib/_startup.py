from ghostlines.toolbar.manager import Manager
from ghostlines.toolbar.release_menu_item import ReleaseMenuItem
from ghostlines.toolbar.comments_menu_item import CommentsMenuItem


Manager(ReleaseMenuItem, index=-2).on("fontDidOpen", "newFontDidOpen")
Manager(CommentsMenuItem, index=-2).on("fontDidOpen", "newFontDidOpen")
