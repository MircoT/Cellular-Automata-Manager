import json
from collections import deque
from ca_entities import ALL_ENTITIES
from ca_base_entity import VoidEntity, ENTITIES_NAMES, ENTITIES_IDS, Point, NEIGHBORHOOD_TYPES
from ca_link import LINK_TYPE_NAMES, LINK_TYPE_IDS
from utils import rotate_point, debug, Point
from collections import defaultdict

from six import add_metaclass
from os import path


class BaseGrid(defaultdict):

    """The base object to memorize all entities
    """

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            # Factory of a Void entity
            ret = self[key] = self.default_factory(VoidEntity().type)
            return ret


class HistoryExtension(object):

    """Extension for CellularGrid to manage history of actions
    """

    def undo(self):
        """Undo last action
        """
        # DEBUG
        #debug("undo", ("actions", self._actions_dicts))
        if self._actions_index > 0:
            # DEBUG
            #debug("undo before clear", ("dict", self._grid))
            self.clear()
            # DEBUG
            #debug("undo after clear", ("dict", self._grid))
            for point, entity in self._actions_dicts[self._actions_index - 1].viewitems():
                self.insert(point, entity)
            self._actions_index -= 1
        # DEBUG
        #debug("undo exit", ("dict", self._grid))

    def redo(self):
        """Redo previous action
        """
        # DEBUG
        #debug("redo", ("actions", self._actions_dicts))
        if self._actions_index + 1 < len(self._actions_dicts):
            self.clear()
            for point, entity in self._actions_dicts[self._actions_index + 1].viewitems():
                self.insert(point, entity)
            self._actions_index += 1

    def push_actions(self):
        """Add last action to the history
        """
        # DEBUG
        #debug("push_actions", ("actions", self._actions_dicts))
        while len(self._actions_dicts) != self._actions_index + 1:
            self._actions_dicts.pop()
        if len(self._actions_dicts) <= self._max_actions:
            self._actions_dicts.append(dict((point, entity_t) for point, entity_t in self._grid.viewitems(
            ) if entity_t != ENTITIES_NAMES['void']))
            self._actions_index += 1
        else:
            self._actions_dicts.popleft()
            self._actions_dicts.append(dict((point, entity_t) for point, entity_t in self._grid.viewitems(
            ) if entity_t != ENTITIES_NAMES['void']))

    def actions_status(self):
        """Return the current len of history action and the current index
        """
        return (len(self._actions_dicts), self._actions_index)


class HistoryMetaclass(type):

    """Metaclass that extend CellularGrid when
    we require an history actions manager
    """
    def __call__(cls, *args, **kwargs):
        if kwargs and kwargs.get('history', False):
            kwargs.pop('history')
            instance = type(
                cls.__name__, (HistoryExtension,), cls.__dict__.copy())
            setattr(instance, "_actions_dicts", deque())
            setattr(instance, "_actions_index", 0)
            setattr(instance, "_max_actions", 10)
            instance._actions_dicts.append(BaseGrid(int).copy())
            return instance.__call__(*args, **kwargs)
        instance = type(cls.__name__, (object,), cls.__dict__.copy())
        return instance.__call__(*args, **kwargs)


@add_metaclass(HistoryMetaclass)
class CellularGrid(object):

    """Object that manage the grid and his entities
    """

    def __init__(self):
        self._grid = BaseGrid(int)
        self._grid_sel = BaseGrid(int)
        self._linked_grids = dict()
        self._linked_names = dict()
        self._links = dict()
        self._my_links = dict()
        self.__actions = {
            'del': list(),
            'ins': list()
        }
        self.__selection_list = list()
        self.__selected_my_links = list()
        self.__selected_links = list()
        self.__all_selection = list()
        self.__speed = 1
        self.__step = -1
        self.__filename = None

    ##
    # Speed section -----------------------------------------------------------
    def get_speed(self):
        """Returns the speed multiplicator for the current grid
        """
        return self.__speed

    def set_speed(self, speed):
        """Sets the speed multiplicator for the current grid
        """
        self.__speed = speed

    def set_grid_speed(self, id_, speed):
        """Sets the speed multiplicator for a linked grid
        """
        self._linked_grids[id_].set_speed(speed)

    ##
    # Link section ------------------------------------------------------------
    def insert_link(self, pos, type_, mylink, id_=None, id_pos=None):
        """Inserts a grid link
        """
        if mylink:
            if type_ == LINK_TYPE_NAMES["IN"]:
                self._my_links[pos] = LINK_TYPE_NAMES["IN"]
            elif type_ == LINK_TYPE_NAMES["OUT"]:
                self._my_links[pos] = LINK_TYPE_NAMES["OUT"]
        else:
            if type_ == LINK_TYPE_NAMES["IN"]:
                self._links[pos] = (LINK_TYPE_NAMES["IN"], id_, id_pos)
            elif type_ == LINK_TYPE_NAMES["OUT"]:
                self._links[pos] = (LINK_TYPE_NAMES["OUT"], id_, id_pos)
        #debug("insert_link", ("my_links", self._my_links), ("links", self._links))

    def delete_link(self, pos):
        """Deletes a link in a specific position
        """
        # DEBUG
        #debug("delete_link", ("cond", pos in self._my_links.viewkeys()))
        if pos in self._my_links.viewkeys():
            temp = self._my_links.pop(pos)
            del temp
        if pos in self._links.viewkeys():
            temp = self._links.pop(pos)
            del temp

    def clear_links(self):
        """Deletes all the links from the current grid
        """
        self._linked_grids.clear()
        self._linked_names.clear()
        self._links.clear()
        self._my_links.clear()

    def get_my_links_list(self):
        """Returns a list of links that belong to the current grid
        with their types
        """
        return [(pos, type_) for pos, type_ in self._my_links.viewitems()]

    def get_linked_grids(self):
        """Generates a list of attribute for each grid linked
        """
        for id_, grid in self._linked_grids.viewitems():
            yield (id_, grid.get_my_links_list(), self._linked_names[id_], grid.speed)

    def update_linked_grids(self):
        """Returns the id and filename attribute for each linked grid
        """
        for id_, grid in self._linked_grids.viewitems():
            new_grid = CellularGrid()
            new_grid.load(grid.filename)
            old_grid = self._linked_grids.pop(id_)
            del old_grid
            self._linked_grids[id_] = new_grid
            links_to_delete = list()
            for pos, data in self._links.viewitems():
                type_, id_l, id_pos_l = data
                if id_l == id_:
                    if not (id_pos_l in new_grid._my_links):
                        links_to_delete.append(pos)
            for pos in links_to_delete:
                self.delete_link(pos)

    def get_my_links(self):
        """Generates a tuple (position, type) for each link of the current grid
        """
        for pos, type_ in self._my_links.viewitems():
            # DEBUG
            #debug("get_links", ("link", (pos, type_)))
            yield (pos, type_)

    def get_links(self):
        """Generates a tuple (position, type, id, position on source grid)
        for each link of the linked grids
        """
        for pos, data in self._links.viewitems():
            type_, id_, id_pos = data
            yield (pos, type_, id_, id_pos)

    def insert_grid(self, filename):
        """Inserts a linked grid
        """
        link_grid = CellularGrid()
        link_grid.load(filename=filename)
        self._linked_grids[id(link_grid)] = link_grid
        self._linked_names[id(link_grid)] = path.split(filename)[-1]
        # DEBUG
        #debug("insert_grid", ("linked_grids", self._linked_grids))

    def delete_grid(self, id_):
        """Deletes a linked grid
        """
        grid = self._linked_grids.pop(id_)
        del grid
        name = self._linked_names.pop(id_)
        del name
        for key, value in self._links.items():
            if value[1] == id_:
                temp = self._links.pop(key)
                del temp
        # DEBUG
        #debug("delete_grid", ("linked_grids", self._linked_grids))

    ##
    # Transformations section ------------------------------------------------
    def rotate(self, deg=90):
        """Rotates the entities selected and
        update the selction list
        """
        if len(self.__selection_list) == 0:
            return
        max_ = max(self.__all_selection)
        min_ = min(self.__all_selection)
        pivot = Point(
            min_.x + ((max_.x - min_.x) / 2.),
            min_.y + ((max_.y - min_.y) / 2.),
        )
        new_dict = BaseGrid(int)
        new_selection = list()
        new_all = list()
        for point in self.__selection_list:
            new_pos = rotate_point(point, pivot, deg)
            new_selection.append(new_pos)
            new_dict[new_pos] = ALL_ENTITIES[self._grid[point]].rotate(deg)
            self.delete(point)
        self.__selection_list = new_selection
        self.__all_selection = list()
        for point in self.__all_selection:
            new_all.append(rotate_point(point, pivot, deg))
        self.__all_selection = new_all
        for pos, entity in self._grid.viewitems():
            if pos not in new_dict:
                new_dict[pos] = entity
        self._grid.clear()
        self._grid.update(new_dict)
        self.__update_selection()

    def flip_h(self):
        """Flips horizontally the entities selected
        and update the selection list
        """
        # DEBUG
        #debug("flip_h", ("selection", self.__selection_list))
        max_x = max(self.__all_selection)[0]
        min_x = min(self.__all_selection)[0]
        mid_x = (max_x - min_x) / 2
        new_dict = BaseGrid(int)
        for point in self.__selection_list:
            my_x, my_y = point
            if my_x > mid_x:
                new_x = min_x + (max_x - my_x)
            else:
                new_x = max_x - (my_x - min_x)
            new_pos = Point(new_x, my_y)
            new_dict[new_pos] = ALL_ENTITIES[self._grid[point]].flip_h()
            self.delete(point)
        for pos, entity in self._grid.viewitems():
            if pos not in new_dict and pos not in self.__selection_list:
                new_dict[pos] = entity
        self._grid.clear()
        self._grid.update(new_dict)
        self.__update_selection()

    def flip_v(self):
        """Flips vertically the entities selected
        and update the selection list
        """
        max_y = max(self.__all_selection)[1]
        min_y = min(self.__all_selection)[1]
        mid_y = (max_y - min_y) / 2
        new_dict = BaseGrid(int)
        for point in self.__selection_list:
            my_x, my_y = point
            if my_y > mid_y:
                new_y = min_y + (max_y - my_y)
            else:
                new_y = max_y - (my_y - min_y)
            new_pos = Point(my_x, new_y)
            new_dict[new_pos] = ALL_ENTITIES[self._grid[point]].flip_v()
            self.delete(point)
        for pos, entity in self._grid.viewitems():
            if pos not in new_dict:
                new_dict[pos] = entity
        self._grid.clear()
        self._grid.update(new_dict)
        self.__update_selection()

    ##
    # Edit section ------------------------------------------------------------
    def delete_selected_entities(self, links=False):
        """Deletes all selected entities
        """
        if links:
            for point in self.__selected_my_links:
                self.delete_link(point)
            for point in self.__selected_links:
                self.delete_link(point)
        else:
            entities = False
            for point in self.__selection_list:
                if not entities:
                    entities = not entities
                self.delete(point)
            return entities

    def move_selected_entities(self, x, y):
        """Moves all selected entities
        """
        new_selection = list()
        new_all = list()
        new_dict = BaseGrid(int)
        for pos in self.__selection_list:
            new_pos = Point(pos.x - x, pos.y - y)
            # DEBUG
            #debug("move_selected_entities", ("NEW POS", new_pos != pos))
            if new_pos != pos:
                new_selection.append(new_pos)
                new_dict[new_pos] = self._grid_sel.pop(pos)
            else:
                return
        self._grid_sel = new_dict
        self.__all_selection = list()
        for point in self.__all_selection:
            new_all.append(Point(point.x - x, point.y - y))
        self.__all_selection = new_all
        # DEBUG
        #debug("move_selected_entities", ("NEW SELECTION", new_selection))
        if len(new_selection) != 0:
            self.__selection_list = new_selection

    def move_all(self, x, y):
        """Moves the entire grid and simulates view motion
        """
        new_dict = dict()
        for pos in self._my_links.viewkeys():
            new_pos = Point(pos.x - x, pos.y - y)
            new_dict[new_pos] = self._my_links[pos]
        self._my_links.clear()
        self._my_links = new_dict
        new_dict = dict()
        for pos in self._links.viewkeys():
            new_pos = Point(pos.x - x, pos.y - y)
            new_dict[new_pos] = self._links[pos]
        self._links.clear()
        self._links = new_dict
        new_dict = BaseGrid(int)
        for pos, entity_t in self._grid.viewitems():
            new_pos = Point(pos.x - x, pos.y - y)
            new_dict[new_pos] = entity_t
        self._grid = new_dict
        new_dict = BaseGrid(int)
        for pos, entity_t in self._grid_sel.viewitems():
            new_pos = Point(pos.x - x, pos.y - y)
            new_dict[new_pos] = entity_t
        self._grid_sel = new_dict
        self.__update_selection()

    def load_selection(self):
        """Loads selected entities on the clipboard
        """
        # DEBUG
        # debug("load_selection")
        for point in self.__selection_list:
            # DEBUG
            #debug("load_selection", ("dict point", self._grid[point]))
            self._grid_sel[point] = self._grid.pop(point)

    def store_selection(self):
        """Stores the clipboard entities on the grid
        """
        # DEBUG
        # debug("store_selection")
        #debug("store_selection", ("ALL", self.__all_selection))
        #debug("store_selection", ("SEL", self.__selection_list))
        #debug("store_selection", ("DICT SEL", self._grid_sel))
        entities_to_ins = list()
        for point in self.__all_selection:
            self.delete(point)
            try:
                entities_to_ins.append((point, self._grid_sel.pop(point)))
            except KeyError:
                self.insert(point, VoidEntity().type)
        for point, entity_t in entities_to_ins:
            self.insert(point, entity_t)
        # self.update_neighbors()

    def clear_selection(self):
        """Clears the current selection
        """
        # DEBUG
        #debug("clear_selection", ("selection list", self.__selection_list))
        del self.__selection_list[:]
        del self.__selected_my_links[:]
        del self.__selected_links[:]
        #self._grid_sel = BaseGrid()

    def __update_selection(self):
        """Updates the current selection
        """
        if len(self.__selection_list) != 0:
            self.clear_selection()
            self.select_entities(self.__all_selection)

    def select_entities(self, item_list):
        """Selects entities in the selection area 
        """
        # DEBUG
        #debug("select_entities", ("Item list", item_list))
        self.__all_selection = item_list
        sel_list_app = self.__selection_list.append  # Speedup append method
        # Speedup append method
        sel_list_mylinks_app = self.__selected_my_links.append
        # Speedup append method
        sel_list_links_app = self.__selected_links.append
        entities_points = [point for point, entity_t in self._grid.viewitems(
        ) if entity_t != ENTITIES_NAMES["void"] and entity_t != ENTITIES_NAMES["deadcell"]]
        # if len(self._grid_sel) == 0:
        # DEBUG
        #debug("select_entities", ("item_list", item_list))
        for point in item_list:
            # DEBUG
            #debug("select_entities", ("POINT IN SELECTION", point not in self.__selection_list))
            if point in entities_points and point not in self.__selection_list:
                # DEBUG
                #debug("select_entities", ("POINT IN SELECTION", point))
                sel_list_app(point)
            elif point in self._my_links:
                sel_list_mylinks_app(point)
            elif point in self._links:
                sel_list_links_app(point)

    ##
    # Get section -------------------------------------------------------------
    def __getattr__(self, attr):
        if attr == "filename":
            return self.__filename
        elif attr == "speed":
            return self.__speed

    def __getitem__(self, pos):
        """Access to the grid like a container (readonly)
        """
        return self._grid[pos]

    def get_entities_to_copy(self):
        """Return a list of (pos, type) for each entity selected
        """
        return [(pos, self._grid[pos]) for pos in self.__selection_list]

    def get_entities(self):
        """Generates a list of non void entities and their position
        """
        for position, entity_t in self._grid.viewitems():
            if entity_t != ENTITIES_NAMES["void"]:
                yield (position, entity_t)

        for position, entity_t in self._grid_sel.viewitems():
            if entity_t != ENTITIES_NAMES["void"]:
                yield (position, entity_t)

    def get_selection_entities_points(self):
        """Return a list of points for non void entities
        """
        return [point for point in self.__selection_list]

    ##
    # Grid actions section ----------------------------------------------------
    def update(self):
        """Updates the entities on the grid with their specific actions
        """
        self.__step += 1

        # LINK UPDATE ----- count_step
        #self._links[pos] = (LINK_TYPE_NAMES["OUT"], id_, id_pos)
        # Check links IN
        in_id = LINK_TYPE_NAMES["IN"]
        for pos, data in self._links.viewitems():
            type_, id_, id_pos = data
            if type_ == in_id:
                self._linked_grids[id_].insert(id_pos, self._grid[pos])

        # Steps of linked grids
        for grid in self._linked_grids.viewvalues():
            if self.speed == grid.speed:
                grid.update()
            elif self.speed < grid.speed:
                step = float(self.speed) / float(grid.speed)
                cond = step
                while cond <= float(self.speed):
                    # DEBUG
                    #debug("UPDATE sub ===")
                    grid.update()
                    cond += step
            # self.speed > grid.speed:
            elif self.speed == grid.speed + self.__step:
                    # DEBUG
                    #debug("UPDATE sub")
                grid.update()

        # Step of the grid
        # DEBUG
        #debug("=== UPDATE" + self.filename)
        void_id = ENTITIES_NAMES['void']
        for pos, entity_t in self._grid.items():
            if entity_t != void_id:
                ALL_ENTITIES[entity_t].step(self, pos)

        # DEBUG
        #debug("update", ("id", id(self)), ("list", self.__actions))
        for pos in self.__actions['del']:
            self.delete(pos)

        for pos, type_ in self.__actions['ins']:
            self.insert(pos, type_)

        if self.__step == self.speed - 1:
            self.__step = -1

        # Update link out
        out_id = LINK_TYPE_NAMES["OUT"]
        for pos, data in self._links.viewitems():
            type_, id_, id_pos = data
            if type_ == out_id:
                self.insert(pos, self._linked_grids[id_][id_pos])

        self.__update_selection()
        del self.__actions['del'][:]
        del self.__actions['ins'][:]

    def insert_action(self, action):
        """Inserts an action that will be processed by the grid
        action = tuple(command, position)
        """
        com, pos = action
        if com in self.__actions:
            if pos not in self.__actions[com]:
                self.__actions[com].append(pos)

    def insert(self, pos, type_):
        """Inserts an entity on the grid
        """
        # DEBUG
        #debug("insert", ("pos", pos), ("type", type_))
        entity_t = None
        if self._grid[pos] != type_:
            entity_t = ALL_ENTITIES[type_].type
        else:
            return  # Entity already exist
        self._grid[pos] = entity_t
        if ALL_ENTITIES[entity_t].neighborhood is not None:
            if ALL_ENTITIES[entity_t].neighborhood == NEIGHBORHOOD_TYPES["moore"]:
                x, y = pos
                for new_x in range(x - 1, x + 2):
                    for new_y in range(y - 1, y + 2):
                        pos = Point(new_x, new_y)
                        if self._grid[pos] != entity_t:
                            self._grid[pos] = ALL_ENTITIES[entity_t].neighbors
            elif ALL_ENTITIES[entity_t].neighborhood == NEIGHBORHOOD_TYPES["1D"]:
                x, y = pos
                for new_x in range(-1, 2, 2):
                    pos = Point(x + new_x, y)
                    if self._grid[pos] != entity_t:
                        self._grid[pos] = ALL_ENTITIES[entity_t].neighbors

    def delete(self, pos):
        """Deletes an entity from the grid
        """
        # DEBUG
        #debug("delete", ("Delete", pos))
        if pos in self._grid:
            temp_type = self._grid.pop(pos)
            if temp_type == ENTITIES_NAMES["livingcell"]:
                self._grid[pos] = ALL_ENTITIES[ENTITIES_NAMES['deadcell']].type
            else:
                self._grid[pos] = VoidEntity().type
            del temp_type
            # DEBUG
            # debug("DELETE!!!")
            #debug("delete", ("void", VoidEntity().type), ("entity", self._grid[pos].type))
            # debug("DELETE!!!")

    def clear(self):
        """Clears the current grid
        """
        self._grid.clear()

    def clear_sparks(self):
        """Deletes all sparks on the grid
        """
        for pos, entity_t in self._grid.viewitems():
            if entity_t == ENTITIES_NAMES["spark"]:
                self.delete(pos)

    ##
    # Marshalling section -----------------------------------------------------
    def store(self, filename="stored.cg"):
        """Saves into a file the current grid
        """
        store_dict = dict()
        for point, entity_t in self._grid.viewitems():
            try:
                store_dict[ENTITIES_IDS[entity_t]].append(point)
            except KeyError:
                store_dict[ENTITIES_IDS[entity_t]] = list()
                store_dict[ENTITIES_IDS[entity_t]].append(point)
        store_dict["my_links"] = dict()
        for point, link in self._my_links.viewitems():
            try:
                store_dict["my_links"][LINK_TYPE_IDS[link]].append(point)
            except KeyError:
                store_dict["my_links"][LINK_TYPE_IDS[link]] = list()
                store_dict["my_links"][LINK_TYPE_IDS[link]].append(point)
        if len(self._links) > 0:
            store_dict["links"] = dict()
            for point, data in self._links.viewitems():
                store_dict["links"]["%s,%s" % point] = data
        if len(self._linked_grids) > 0:
            store_dict["linked_names"] = dict()
            for id_, name in self._linked_names.viewitems():
                store_dict["linked_names"][str(id_)] = name

        with open(filename, "w") as fp:
            json.dump(store_dict, fp)
        #self._linked_grids = dict()
        #self._linked_names = dict()
        #self._links = dict() (LINK_TYPE_NAMES["IN"], id_, id_pos)

    def load(self, filename="stored.cg"):
        """Loads a grid from a file
        """
        base_path = path.dirname(filename)
        #base_path = "/".join(filename.split("/")[:-1])
        # DEBUG
        #debug("load", ("base_path", base_path), ("filename", filename))
        self.__filename = filename

        with open(filename, "r") as fp:
            stored_dict = json.load(fp)

        for type_, list_ in stored_dict.viewitems():
            if type_ == "my_links":
                for sub_type, sub_list in list_.viewitems():
                    for pos in sub_list:
                        pos = Point(pos[0], pos[1])
                        if sub_type == LINK_TYPE_IDS[LINK_TYPE_NAMES["IN"]]:
                            self.insert_link(pos, LINK_TYPE_NAMES["IN"], True)
                        elif sub_type == LINK_TYPE_IDS[LINK_TYPE_NAMES["OUT"]]:
                            self.insert_link(pos, LINK_TYPE_NAMES["OUT"], True)
            # "links": {"10,6": [[-1, 36574928, [12, 5]]]}
            elif type_ == "links":
                added = dict()
                grids_container = dict()
                for point, data in list_.viewitems():
                    pos = map(int, point.split(","))
                    pos = Point(pos[0], pos[1])
                    type_, id_, id_pos = data
                    id_pos = Point(id_pos[0], id_pos[1])
                    if id_ not in added:
                        new_grid = CellularGrid()
                        new_grid.load(
                            path.join(base_path, stored_dict["linked_names"][str(id_)]))
                        added[id_] = id(new_grid)
                        grids_container[id_] = new_grid
                    self._linked_names[added[id_]] = stored_dict[
                        "linked_names"][str(id_)]
                    self._linked_grids[added[id_]] = grids_container[id_]
                    self._links[pos] = (type_, added[id_], id_pos)
            elif type_ in ENTITIES_NAMES:
                for pos in list_:
                    pos = Point(pos[0], pos[1])
                    self.insert(pos, ENTITIES_NAMES[type_])
