class DeferredWindow(object):

    def __init__(self, window, *args, **kwargs):
        self.window = window
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.window(*self.args, **self.kwargs)
