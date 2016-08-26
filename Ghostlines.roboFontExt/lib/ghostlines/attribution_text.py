from vanilla import TextBox

from AppKit import NSFontAttributeName, NSFont, NSForegroundColorAttributeName, NSColor, NSMutableAttributedString


class AttributionText(TextBox):

    def __init__(self, dimensions, font):
        font_name = font.info.familyName
        attribution = "{} by {}".format(font_name, font.info.designer)
        attribution_attributes = {
            NSFontAttributeName: NSFont.systemFontOfSize_(NSFont.systemFontSize()),
            NSForegroundColorAttributeName: NSColor.whiteColor()
        }
        formatted_attribution = NSMutableAttributedString.alloc().initWithString_attributes_(attribution, attribution_attributes)
        formatted_attribution.addAttribute_value_range_(NSFontAttributeName, NSFont.boldSystemFontOfSize_(NSFont.systemFontSize()), [0, len(font_name)])

        super(AttributionText, self).__init__(dimensions, formatted_attribution)
