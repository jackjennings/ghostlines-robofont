from vanilla import ImageView

from AppKit import NSImage, NSBezierPath, NSMakeRect, NSColor


class DashedRectangle(ImageView):

    def __init__(self, dimensions):
        super(DashedRectangle, self).__init__(dimensions, scale="none")

        box_width = self.getPosSize()[2]
        box_height = self.getPosSize()[3]

        line_image = NSImage.alloc().initWithSize_((box_width, box_height))
        line_image.lockFocus()
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(NSMakeRect(.5, .5, box_width - 1, box_height - 1), 5, 5)
        path.setLineWidth_(1.0)
        path.setLineDash_count_phase_((5, 5), 2, 0)
        NSColor.colorWithCalibratedWhite_alpha_(0, 0.1).set()
        path.stroke()
        line_image.unlockFocus()

        self.setImage(imageObject=line_image)
