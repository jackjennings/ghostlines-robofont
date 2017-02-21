from vanilla import ImageView

from AppKit import NSImage, NSColor, NSRectFillUsingOperation, NSCompositeSourceOver


class Background(ImageView):

    def __init__(self, dimensions):
        super(Background, self).__init__(dimensions, scale="fit")

        colorTile = NSImage.alloc().initWithSize_((10, 10))
        colorTile.lockFocus()
        color = NSColor.colorWithCalibratedWhite_alpha_(0, 0.05)
        color.set()
        NSRectFillUsingOperation(((0, 0), (10, 10)), NSCompositeSourceOver)
        colorTile.unlockFocus()

        self.setImage(imageObject=colorTile)
