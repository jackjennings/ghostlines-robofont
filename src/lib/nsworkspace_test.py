from AppKit import NSWorkspace

print NSWorkspace.sharedWorkspace().iconForFileType_("txt")