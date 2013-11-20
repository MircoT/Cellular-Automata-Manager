from .ca_base_entity import BaseEntity, VoidEntity, ENTITIES_NAMES, NEIGHBORHOOD_TYPES
from .utils import Point


class MonoOne(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(MonoOne, self).__init__(
            ENTITIES_NAMES['monoone'],
            NEIGHBORHOOD_TYPES["1D"],
            ENTITIES_NAMES["monozero"]
        )
    
    def step(self, grid, pos):
        if self.get_neighbor(grid, pos, 'S') != ENTITIES_NAMES["void"]:
            return
        right = self.get_neighbor(grid, pos, 'E')
        left = self.get_neighbor(grid, pos, 'W')
        out = False
        if right == ENTITIES_NAMES["monozero"] and\
            left == ENTITIES_NAMES["monozero"]: # 010
            out = True
        elif right == ENTITIES_NAMES["monozero"] and\
            left == ENTITIES_NAMES["monoone"]: # 110
            out = False
        elif right == ENTITIES_NAMES["monoone"] and\
            left == ENTITIES_NAMES["monozero"]: # 011
            out = True
        elif right == ENTITIES_NAMES["monoone"] and\
            left == ENTITIES_NAMES["monoone"]: # 111
            out = False
        my_x, my_y = pos
        dif_x, dif_y = self.neighborhood_pos['S']
        new_pos = Point(my_x + dif_x, my_y + dif_y)
        if out: 
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["monoone"])))
        else:
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["monozero"])))

class MonoZero(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(MonoZero, self).__init__(ENTITIES_NAMES['monozero'])
    def step(self, grid, pos):
        if self.get_neighbor(grid, pos, 'S') != ENTITIES_NAMES["void"]:
            return
        right = self.get_neighbor(grid, pos, 'E')
        left = self.get_neighbor(grid, pos, 'W')
        out = False
        if left == ENTITIES_NAMES["void"]:
            left = ENTITIES_NAMES["monozero"]
        if right == ENTITIES_NAMES["void"]:
            right = ENTITIES_NAMES["monozero"]
        if right == ENTITIES_NAMES["monoone"] and\
            left == ENTITIES_NAMES["monoone"]: # 101
            out = False
        elif right == ENTITIES_NAMES["monozero"] and\
            left == ENTITIES_NAMES["monoone"]: # 100
            out = True
        elif right == ENTITIES_NAMES["monoone"] and\
            left == ENTITIES_NAMES["monozero"]: # 001
            out = True
        elif right == ENTITIES_NAMES["monozero"] and\
            left == ENTITIES_NAMES["monozero"]: # 000
            out = False
        my_x, my_y = pos
        dif_x, dif_y = self.neighborhood_pos['S']
        new_pos = Point(my_x + dif_x, my_y + dif_y)
        if out: 
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["monoone"])))
        else:
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["monozero"])))

class LivingCell(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(LivingCell, self).__init__(
            ENTITIES_NAMES['livingcell'],
            NEIGHBORHOOD_TYPES["moore"],
            ENTITIES_NAMES["deadcell"])

    def step(self, grid, pos):
        if [self.get_neighbor(grid, pos, 'N'),
            self.get_neighbor(grid, pos, 'NE'),
            self.get_neighbor(grid, pos, 'E'),
            self.get_neighbor(grid, pos, 'SE'),
            self.get_neighbor(grid, pos, 'S'),
            self.get_neighbor(grid, pos, 'SW'),
            self.get_neighbor(grid, pos, 'W'),
            self.get_neighbor(grid, pos, 'NW')].count(ENTITIES_NAMES['livingcell']) in [2, 3]:
            return
        else:
            grid.insert_action(("del", pos))

class DeadCell(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(DeadCell, self).__init__(ENTITIES_NAMES['deadcell'])
    
    def step(self, grid, pos):
        if [self.get_neighbor(grid, pos, 'N'),
            self.get_neighbor(grid, pos, 'NE'),
            self.get_neighbor(grid, pos, 'E'),
            self.get_neighbor(grid, pos, 'SE'),
            self.get_neighbor(grid, pos, 'S'),
            self.get_neighbor(grid, pos, 'SW'),
            self.get_neighbor(grid, pos, 'W'),
            self.get_neighbor(grid, pos, 'NW')].count(ENTITIES_NAMES['livingcell']) == 3:
            grid.insert_action(("ins", (pos, ENTITIES_NAMES["livingcell"])))

class Spark(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(Spark, self).__init__(ENTITIES_NAMES['spark'])
    
    def step(self, grid, pos):
        grid.insert_action(("del", pos))

class ArrowUp(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(ArrowUp, self).__init__(ENTITIES_NAMES['arrowup'])
    
    def rotate(self, deg):
        if deg == 90:
            return ENTITIES_NAMES['arrowright']
        elif deg == 180:
            return ENTITIES_NAMES['arrowdown']
        elif deg == 270:
            return ENTITIES_NAMES['arrowleft']
    
    def flip_v(self):
        return ENTITIES_NAMES['arrowdown']
    
    def step(self, grid, pos):
        results = False
        if self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
                return
            elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
            results = True
        if not results:
            return
        next_pos = self.get_neighbor(grid, pos, 'N') == ENTITIES_NAMES["spark"] or\
            self.get_neighbor(grid, pos, 'N') == ENTITIES_NAMES["void"]
        if results and next_pos:
            my_x, my_y = pos
            dif_x, dif_y = self.neighborhood_pos['N']
            new_pos = Point(my_x + dif_x, my_y + dif_y)
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["spark"])))


class ArrowDown(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(ArrowDown, self).__init__(ENTITIES_NAMES['arrowdown'])
    
    def rotate(self, deg):
        if deg == 90:
            return ENTITIES_NAMES['arrowleft']
        elif deg == 180:
            return ENTITIES_NAMES['arrowup']
        elif deg == 270:
            return ENTITIES_NAMES['arrowright']
    
    def flip_v(self):
        return ENTITIES_NAMES['arrowup']
    
    def step(self, grid, pos):
        results = False
        if self.get_neighbor(grid, pos, 'N') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
                return
            elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
            results = True
        if not results:
            return
        next_pos = self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"] or\
            self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["void"]
        if results and next_pos:
            my_x, my_y = pos
            dif_x, dif_y = self.neighborhood_pos['S']
            new_pos = Point(my_x + dif_x, my_y + dif_y)
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["spark"])))


class ArrowRight(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(ArrowRight, self).__init__(ENTITIES_NAMES['arrowright'])
    
    def rotate(self, deg):
        if deg == 90:
            return ENTITIES_NAMES['arrowdown']
        elif deg == 180:
            return ENTITIES_NAMES['arrowleft']
        elif deg == 270:
            return ENTITIES_NAMES['arrowup']
    
    def flip_h(self):
        return ENTITIES_NAMES['arrowleft']
    
    def step(self, grid, pos):
        results = False
        if self.get_neighbor(grid, pos, 'N') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"]:
                return
            elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"]:
            results = True
        if not results:
            return
        next_pos = self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"] or\
            self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["void"]
        if results and next_pos:
            my_x, my_y = pos
            dif_x, dif_y = self.neighborhood_pos['E']
            new_pos = Point(my_x + dif_x, my_y + dif_y)
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["spark"])))


class ArrowLeft(BaseEntity):
    def __init__(self, *args, **kwargs):
        super(ArrowLeft, self).__init__(ENTITIES_NAMES['arrowleft'])
    
    def rotate(self, deg):
        if deg == 90:
            return ENTITIES_NAMES['arrowup']
        elif deg == 180:
            return ENTITIES_NAMES['arrowright']
        elif deg == 270:
            return ENTITIES_NAMES['arrowdown']
    
    def flip_h(self):
        return ENTITIES_NAMES['arrowright']
    
    def step(self, grid, pos):
        results = False
        if self.get_neighbor(grid, pos, 'N') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"]:
                return
            elif self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'S') == ENTITIES_NAMES["spark"]:
            if self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
                return
            else:
                results = True
        elif self.get_neighbor(grid, pos, 'E') == ENTITIES_NAMES["spark"]:
            results = True
        if not results:
            return
        next_pos = self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["spark"] or\
            self.get_neighbor(grid, pos, 'W') == ENTITIES_NAMES["void"]
        if results and next_pos:
            my_x, my_y = pos
            dif_x, dif_y = self.neighborhood_pos['W']
            new_pos = Point(my_x + dif_x, my_y + dif_y)
            grid.insert_action(("ins", (new_pos, ENTITIES_NAMES["spark"])))

#####
# All Entities
ALL_ENTITIES = {
    ENTITIES_NAMES['void']: VoidEntity(),
    ENTITIES_NAMES['spark']: Spark(),
    ENTITIES_NAMES['arrowup']: ArrowUp(),
    ENTITIES_NAMES['arrowdown']: ArrowDown(),
    ENTITIES_NAMES['arrowright']: ArrowRight(),
    ENTITIES_NAMES['arrowleft']: ArrowLeft(),
    ENTITIES_NAMES['livingcell']: LivingCell(),
    ENTITIES_NAMES['deadcell']: DeadCell(),
    ENTITIES_NAMES['monoone']: MonoOne(),
    ENTITIES_NAMES['monozero']: MonoZero()
}