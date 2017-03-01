from ghostlines.toolbar.manager import Manager
from ghostlines.toolbar.release_menu_item import ReleaseMenuItem


Manager(ReleaseMenuItem, index=-2).on("fontDidOpen", "newFontDidOpen")
