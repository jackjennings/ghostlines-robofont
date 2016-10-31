from AppKit import NSForegroundColorAttributeName, NSColor, NSAttributedString

def WhiteText(string):
    attributes = {
        NSForegroundColorAttributeName: NSColor.whiteColor()
    }

    return NSAttributedString.alloc().initWithString_attributes_(string, attributes)
