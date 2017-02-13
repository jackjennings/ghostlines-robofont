import os
from AppKit import NSWorkspace, NSLineBreakByTruncatingTail

from vanilla import Group, Button, TextBox, ImageView, ImageButton
from vanilla.dialogs import getFile, message

from ghostlines.storage.null_storage import NullStorage


class FileUploadField(Group):

    def __init__(self, dimensions, storage=NullStorage()):
        self.storage = storage

        super(FileUploadField, self).__init__(dimensions)

        self.choose_file_button = Button((0, 3, 100, 17), "Choose File", sizeStyle="small", callback=self.choose_file)
        self.remove_file_button = Button((-60, 3, 60, 17), "Remove", sizeStyle="small", callback=self.remove_file)
        self.filepath_label = TextBox((18, 3, -70, 20), "")
        self.filepath_button = ImageButton((0, 3, -70, 20), "", callback=self.reveal_file)
        self.filepath_button.getNSButton().setTransparent_(True)
        self.filetype_image = ImageView((0, 4, 16, 16))

        self.filepath = self.storage.retrieve()

    def choose_file(self, sender):
        filepath = getFile("Choose a .txt or .pdf document to use as a license",
                           "Select License",
                           fileTypes=("txt", "md", "pdf"))

        if filepath is not None:
            self.storage.store(filepath[0])
            self.filepath = filepath[0]

    def remove_file(self, sender):
        self.storage.store(None)
        self.filepath = None

    def reveal_file(self, sender):
        workspace = NSWorkspace.sharedWorkspace()
        workspace.selectFile_inFileViewerRootedAtPath_(self.filepath,
                                                       os.path.dirname(self.filepath))

    @property
    def filename(self):
        if self.filepath is not None:
            return os.path.basename(self.filepath)
        else:
            return ""

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, value):
        self._filepath = value

        selected = value is not None and value is not ''

        icon = NSWorkspace.sharedWorkspace().iconForFile_(self._filepath)

        self.choose_file_button.show(not selected)
        self.remove_file_button.show(selected)
        self.filepath_label.show(selected)
        self.filepath_label.set(self.filename)
        self.filepath_button.show(selected)
        self.filetype_image.show(selected)
        self.filetype_image.setImage(imageObject=icon)
