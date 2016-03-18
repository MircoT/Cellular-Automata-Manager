import wx
from .utils import Singleton
from os import path, walk
from six import add_metaclass
from PIL import Image


class Container(dict):

    """Class to store resources
    """

    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        return super(Container, self).__getitem__(name)


@add_metaclass(Singleton)
class ResourceManager(object):

    """Class to manage import of resources
    """

    def __init__(self, basedir="../assets"):
        self.__base_dir = path.abspath(
            path.join(path.dirname(__file__), basedir))
        self.__resources = Container()
        for root, dirs, files in walk(self.__base_dir):
            for file_ in files:
                if file_.split(".")[-1] == "png":
                    # Delete extension and split type from name
                    type_, name = "".join(file_.split(".")[:1]).split("_")
                    if type_ not in self.__resources:
                        self.__resources[type_] = Container()
                    if type_ == "icon":
                        self.__resources[type_][name] = wx.Icon(
                            path.join(root, file_), wx.BITMAP_TYPE_PNG)
                    elif type_ == "entity" or type_ == "tool":
                        self.__resources[type_][name] = Image.open(
                            path.join(root, file_))
                    else:
                        self.__resources[type_][name] = wx.Bitmap(
                            path.join(root, file_), wx.BITMAP_TYPE_PNG)

    def __getattr__(self, name):
        return self.__resources[name]
