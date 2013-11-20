from .utils import Singleton
from six import add_metaclass

@add_metaclass(Singleton)
class StatusBarManager(object):
    def __init__(self, statusbar):
        self.__statusbar = statusbar
        # Set label proportion
        self.__statusbar.SetStatusWidths([-2, -1])
    
    def UpdateStatusBar(self, *args):
        for i in range(len(args)):
            if args[i] is not None:
                self.__statusbar.SetStatusText(args[i], i)