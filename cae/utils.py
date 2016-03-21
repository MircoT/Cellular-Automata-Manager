from math import sin, cos, radians
from collections import namedtuple
import logging

__version__ = "1.1.1"

# Point type
Point = namedtuple("Point", ('x', 'y'))

# Tile size
TS = 16
# Smart selection
SMART_SEL = False


class Singleton(type):

    """Class for the singleton pattern
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def debug(message, *args):
    """Print a debug message if debugging is active
    """
    logger = logging.getLogger()
    if logger.isEnabledFor(logging.DEBUG):
        if len(args) == 0:
            logger.debug(message)
        else:
            logger.debug("[-- %s --", message)
            for item in args:
                name, value = item
                logger.debug(" -- %s -> %s", name, value)
            logger.debug(" --]")


def rotate_point(point, pivot, degrees):
    """Rotate the point for tot degrees respect the pivot
    """
    rad = radians(degrees)
    sin_ = round(sin(rad))
    cos_ = round(cos(rad))
    new_pos = Point(
        point.x - pivot.x,
        point.y - pivot.y
    )
    new_pos = Point(
        new_pos.x * cos_ - new_pos.y * sin_,
        new_pos.x * sin_ + new_pos.y * cos_
    )
    new_pos = Point(
        int(round(new_pos.x + pivot.x)),
        int(round(new_pos.y + pivot.y))
    )
    return new_pos
