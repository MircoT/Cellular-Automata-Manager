import wx
from .utils import debug, Singleton, Point
from .ca_link import LINK_TYPE_IDS, LINK_TYPE_NAMES
from six import add_metaclass
from random import randint

def get_random_color():
    red = randint(0,255)
    green = randint(0,255)
    blue = randint(0,255)
    return (red, green, blue)

class ChangeSpeedDialog(wx.Dialog):
    """Dialog frame to change grids' speed
    """
    def __init__(self, parent, id_=None):
        super(ChangeSpeedDialog, self).__init__(parent, wx.ID_ANY, "Speed")
        self.__parent = parent
        self.__id = id_
        self.text = wx.TextCtrl(self, value="1")
        self.spin = wx.SpinButton(self, style=wx.SP_VERTICAL)
        self.spin.SetRange(1, 100)
        self.spin.SetValue(1)
        self.btn = wx.Button(self, label='Set')
        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv = wx.BoxSizer(wx.VERTICAL)
        sizerh.Add(self.text, 0, wx.CENTER)
        sizerh.Add(self.spin, 0, wx.CENTER)
        sizerv.Add(sizerh, 0, wx.CENTER)
        sizerv.Add(self.btn, 1, wx.CENTER)

        self.SetSizer(sizerv)
        self.SetAutoLayout(True)
        sizerv.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnSet, self.btn)
        self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)
        self.Show()

    def OnSpin(self, event):
        """Spin event
        """
        self.text.SetValue(str(event.GetPosition()))

    def OnSet(self, event):
        """Set event
        """
        self.__parent.SetSpeed(int(self.text.GetValue()), self.__id)
        self.Close()


class MyTreeCtrl(wx.TreeCtrl):
    """Widget to manage imported grids
    """
    def __init__(self, parent, id_, pos, size, style):
        super(MyTreeCtrl, self).__init__(parent, id_, pos, size, style)
        self.item = None
        self.__notman = None
        self.__root = self.AddRoot("Grids")
        self.AppendItem(self.__root, "--- THIS GRID ---")
        self.__mem_color = dict()
        self.__selection = [get_random_color()]
        self.Bind(wx.EVT_LEFT_DOWN, self.OnDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

    def set_notebook(self, notebook):
        """Sets notebook's reference
        """
        self.__notman = notebook
        self.DeleteChildren(self.__root)
        first = self.AppendItem(self.__root, "--- THIS GRID --- with speed = %s" % self.__notman.GetSpeed())
        self.SetItemBackgroundColour(first, get_random_color())

    def OnSelChanged(self, e):
        """Change selection event
        """
        if self.GetSelection().IsOk():
            text = self.GetItemText(self.GetSelection())
            if text.find("->") != -1:
                type_ = id_ = pos = name = None
                parent_text = self.GetItemText(self.GetItemParent(self.GetSelection()))
                name, id_ = parent_text.split(" - with speed =")[0].split(" | id:")
                id_ = int(id_)
                if text.find("from") != -1:
                    type_, pos = text.split(" from -> ")
                    type_ = LINK_TYPE_NAMES[type_]
                    pos = map(int, pos.replace("(", "").replace(")","").split(","))
                    pos = Point(pos[0], pos[1])
                elif text.find("to") != -1:
                    type_, pos = text.split(" to -> ")
                    type_ = LINK_TYPE_NAMES[type_]
                    pos = map(int, pos.replace("(", "").replace(")","").split(","))
                    pos = Point(pos[0], pos[1])
                color = self.GetItemBackgroundColour(self.GetItemParent(self.GetSelection()))
                self.__selection = (color, id_, pos, type_)
            elif text.find("|") != -1:
                name, id_ = text.split(" - with speed =")[0].split(" | id:")
                id_ = int(id_)
                color = self.GetItemBackgroundColour(self.GetSelection())
                self.__selection = (color, id_)
            else:
                color = self.GetItemBackgroundColour(self.GetSelection())
                self.__selection = [color]
            try:
                self.__notman.SetLinkSelection(self.__selection)
            except wx.PyDeadObjectError:
                pass

    def UpdateTree(self):
        """Update the grids' tree
        """
        self.DeleteChildren(self.__root)
        first = self.AppendItem(self.__root, "--- THIS GRID --- with speed = %s" % self.__notman.GetSpeed())
        if "first" not in self.__mem_color:
            self.__mem_color['first'] =  get_random_color()
        self.SetItemBackgroundColour(first, self.__mem_color['first'])
        if self.__notman:
            for id_, links, name, speed in self.__notman.get_linked_grids():
                if id_ not in self.__mem_color:
                    self.__mem_color[id_] =  get_random_color()
                child = self.AppendItem(self.__root, "%s | id:%s - with speed = %s" % (name, id_, speed))
                self.SetItemBackgroundColour(child, self.__mem_color[id_])
                for pos, type_ in links:
                    if type_ == LINK_TYPE_NAMES["IN"]:
                        self.AppendItem(child, "IN to -> (%s,%s)" % pos)
                    elif type_ == LINK_TYPE_NAMES["OUT"]:
                        self.AppendItem(child, "OUT from -> (%s,%s)" % pos)
        self.ExpandAll()

    def UpdateGrids(self, e):
        """Update all imported grids
        """
        self.__notman.update_grids()

    def DeleteGrid(self, e):
        """Delete a grid
        """
        debug("DeleteGrid")
        text = self.GetItemText(self.GetSelection())
        if text == "Grids":
            return
        if text.find("|") == -1:
            text = self.GetItemText(self.GetItemParent(self.GetSelection()))
        name, id_ = text.split(" - with speed =")[0].split(" | id:")
        self.__notman.delete_grid(int(id_))
        self.UpdateTree()

    def InsertGrid(self, e):
        """Insert a grid
        """
        files_types = "Grid Files (*.cg)|*.cg|File di Testo (*.txt)|*.txt|Tutti i Files (*)|*"
        dialog = wx.FileDialog(
            self, message="Open grid file", wildcard=files_types, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
        )
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.__notman.insert_grid(path)
            self.UpdateTree()
        dialog.Destroy()

    def ChangeRandomColor(self, e):
        """Change a color of a selected item randomly
        """
        # DEBUG
        #debug("ChangeRandomColor")
        if self.GetItemText(self.GetSelection()).find("THIS") != -1:
            self.__mem_color['first'] = get_random_color()
            self.SetItemBackgroundColour(self.GetSelection(), self.__mem_color['first'])
        else:
            text = self.GetItemText(self.GetSelection())
            name, id_ = text.split(" - with speed =")[0].split(" | id:")
            self.__mem_color[int(id_)] = get_random_color()
            self.SetItemBackgroundColour(self.GetSelection(), self.__mem_color[int(id_)])
        self.ToggleItemSelection(self.GetSelection())
    
    def OnDown(self, event):
        """On down tree event
        """
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)

        if item:
            self.SelectItem(item)
        else:
            self.__notman.SetLinkSelection(self.__selection)
            self.UnselectAll()
    
    def SetSpeed(self, speed, id_):
        """Set the speed of a grid
        """
        if id_ is None:
            self.__notman.SetSpeed(speed)
        else:
            self.__notman.SetGridsSpeed(speed, id_)
        self.UpdateTree()
    
    def ChangeSpeed(self, event):
        """Calling the dialog to change the speed of a grid
        """
        if len(self.__selection) > 1:
            ChangeSpeedDialog(self, self.__selection[1])
        else:
            ChangeSpeedDialog(self)
            
    def OnRightUp(self, event):
        """On right up tree event
        """
        menu = wx.Menu()
        insert_grid = menu.Append(wx.ID_ANY, "Insert grid")
        self.Bind(wx.EVT_MENU, self.InsertGrid, insert_grid)
        if self.GetSelection().IsOk():
            text = self.GetItemText(self.GetSelection())
            if text.find("THIS GRID") == -1:
                delete_grid = menu.Append(wx.ID_ANY, "Delete grid")
                self.Bind(wx.EVT_MENU, self.DeleteGrid, delete_grid)
        menu.AppendSeparator()
        update_grids = menu.Append(wx.ID_ANY, "Update grids")
        self.Bind(wx.EVT_MENU, self.UpdateGrids, update_grids)
        if self.GetSelection().IsOk():
            text = self.GetItemText(self.GetSelection())
            if text.find("|") != -1 or text.find("THIS GRID") != -1:
                menu.AppendSeparator()
                change_color = menu.Append(wx.ID_ANY, "Change color")
                change_speed = menu.Append(wx.ID_ANY, "Change speed")
                self.Bind(wx.EVT_MENU, self.ChangeRandomColor, change_color)
                self.Bind(wx.EVT_MENU, self.ChangeSpeed, change_speed)
        
        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()

@add_metaclass(Singleton)
class GridTreeCtrl(wx.Dialog):
    """Class to manage tree view of imported grids
    """
    def __init__(self, parent):
        super(GridTreeCtrl, self).__init__(parent, title="Links Manager", size=(400,250), style=wx.CAPTION|wx.STAY_ON_TOP)
        self.__parent = parent
        self._tree = MyTreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, (400,250),
                               wx.TR_DEFAULT_STYLE
                               |wx.TR_LINES_AT_ROOT
                               |wx.TR_FULL_ROW_HIGHLIGHT
                               |wx.TR_SINGLE
                               |wx.TR_HIDE_ROOT
                               #wx.TR_HAS_BUTTONS
                               #| wx.TR_EDIT_LABELS
                               #| wx.TR_MULTIPLE
                               #| wx.TR_HIDE_ROOT
        )
        s = wx.BoxSizer()
        s.Add(self._tree, 0, wx.EXPAND|wx.ALL)
    
    def UpdateTree(self):
        """Update the tree view
        """
        self._tree.UpdateTree()

    def SetNotebook(self, notebook):
        """Set the notebook for the tree
        """
        self._tree.set_notebook(notebook)