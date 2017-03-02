from vanilla.vanillaBase import VanillaBaseObject
from vanilla.nsSubclasses import getNSSubclass

from AppKit import NSURL, NSMutableURLRequest
from WebKit import WKWebView, WKWebViewConfiguration


class WebView(VanillaBaseObject):

    nsViewClass = WKWebView

    def __init__(self, posSize):
        l, t, w, h = posSize
        configuration = WKWebViewConfiguration.alloc().init()
        self._nsObject = getNSSubclass(self.nsViewClass).alloc().initWithFrame_configuration_(((l, t), (w, h)), configuration)
        self._posSize = posSize
        self._setAutosizingFromPosSize(posSize)

    def load(self, url, headers = {}):
        url = NSURL.alloc().initWithString_(url)
        request = NSMutableURLRequest.alloc().initWithURL_(url)

        for header, value in headers.iteritems():
            request.setValue_forHTTPHeaderField_(value, header)

        self._nsObject.loadRequest_(request)

    @property
    def loading(self):
        return self._nsObject.isLoading() == 1
