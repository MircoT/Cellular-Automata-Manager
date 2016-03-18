from .utils import Point, Singleton
from six import add_metaclass

ENTITIES_IDS = {
    0: "void",
    1: "spark",
    2: "arrowup",
    3: "arrowdown",
    4: "arrowright",
    5: "arrowleft",
    6: "livingcell",
    7: "deadcell",
    8: "monoone",
    9: "monozero"
}

ENTITIES_NAMES = dict([(value, key) for key, value in ENTITIES_IDS.items()])

NEIGHBORHOOD_IDS = {
    0: "moore",
    1: "1D"
}

NEIGHBORHOOD_TYPES = dict([(value, key)
                           for key, value in NEIGHBORHOOD_IDS.items()])


@add_metaclass(Singleton)
class VoidEntity():

    """Represents void cells
    """

    def __init__(self):
        self._type = ENTITIES_NAMES['void']

    def __getattr__(self, attr):
        if attr == "type":
            return self._type


class BaseEntity(object):

    """Base class for all entities
    """
    neighborhood_pos = {
        'N': (0, -1),
        'S': (0, 1),
        'E': (1, 0),
        'W': (-1, 0),
        'NE': (1, -1),
        'NW': (-1, -1),
        'SE': (1, 1),
        'SW': (-1, 1),
        'NN': (0, -2),
        'SS': (0, 2),
        'EE': (2, 0),
        'WW': (-2, 0),
    }

    def __init__(self, type_=-1, neighborhood=None, neighbors=None):
        self._type = type_
        self._neighborhood = neighborhood
        self._neighbors = neighbors

    def __eq__(self, other):
        if isinstance(other, BaseEntity):
            return self.type == other.type
        else:
            return False

    def __getattr__(self, attr):
        if attr == "type":
            return self._type
        elif attr == "neighborhood":
            return self._neighborhood
        elif attr == "neighbors":
            return self._neighbors

    def step(self, grid, pos):
        """Virtual method for the progress of the entity
        """
        pass

    def rotate(self, deg):
        """Rotate the entity respect a pivot by deg degrees
        """
        return self._type

    def flip_h(self):
        """Flip an entity horizontally in a portion of the space
        """
        return self._type

    def flip_v(self):
        """Flip the entity vertically in a portion of the space
        """
        return self._type

    def get_neighbor(self, grid, pos, dir_=None):
        """Returns the type of the cell in base to the direction
        """
        if dir_:
            my_x, my_y = pos
            dif_x, dif_y = self.neighborhood_pos[dir_]
            return grid[Point(my_x + dif_x, my_y + dif_y)]
        else:
            return grid[pos]
