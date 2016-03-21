import wx
import wx.aui
from .wxui_draw import DrawWindow
from .ca_grid import CellularGrid
from .ca_base_entity import Point
from .utils import Singleton, debug
from .wxui_staman import StatusBarManager
from os import path
from six import add_metaclass


@add_metaclass(Singleton)
class GridNotebook(wx.aui.AuiNotebook):

    def __init__(self, *args, **kwargs):
        super(GridNotebook, self).__init__(*args, **kwargs)
        self.__parent = args[0]
        self.__ca_list = list()
        self.__ca_loop = list()
        self.__delay = 10
        self.__renderer_list = list()
        self.__clipboard = dict()
        self.__clipboard_pos = Point(-1, -1)
        self.__smart_selection = False
        self.__loop_started = False
        self.__gtree = None
        self.__files_names = list()

        # Events list for AUI notebook:
        # EVT_AUINOTEBOOK_ALLOW_DND
        # EVT_AUINOTEBOOK_BEGIN_DRAG
        # EVT_AUINOTEBOOK_BUTTON
        # EVT_AUINOTEBOOK_DRAG_MOTION
        # EVT_AUINOTEBOOK_END_DRAG
        # EVT_AUINOTEBOOK_PAGE_CHANGED
        # EVT_AUINOTEBOOK_PAGE_CHANGING
        # EVT_AUINOTEBOOK_PAGE_CLOSE
        # EVT_AUI_FIND_MANAGER
        # EVT_AUI_PANE_BUTTON
        # EVT_AUI_PANE_CLOSE
        # EVT_AUI_PANE_MAXIMIZE
        # EVT_AUI_PANE_RESTORE
        # EVT_AUI_RENDER
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.NewGrid()

        # TO SET PAGE NAME
        #self.SetPageText(sel, "Grid %d" % sel)

    def SetGridTree(self, gt):
        """Set the tree reference
        """
        self.__gtree = gt

    def GetSpeed(self):
        """Gets current grid's speed
        """
        return self.__ca_list[self.GetSelection()].get_speed()

    def SetSpeed(self, speed):
        """Sets current grid's speed
        """
        return self.__ca_list[self.GetSelection()].set_speed(speed)

    def SetGridsSpeed(self, speed, id_):
        """Sets the speed for a specific grid
        """
        self.__ca_list[self.GetSelection()].set_grid_speed(id_, speed)

    def SetLinkSelection(self, selection):
        """Set the selected links for the current grid
        """
        self.__renderer_list[self.GetSelection()].set_link_selection(selection)

    def get_linked_grids(self):
        """Get all linked grids
        """
        return self.__ca_list[self.GetSelection()].get_linked_grids()

    def update_grids(self):
        """Update all linked grids
        """
        self.__ca_list[self.GetSelection()].update_linked_grids()
        self.__gtree.UpdateTree()

    def insert_grid(self, filename):
        """Insert a grid in the current grid
        """
        self.__ca_list[self.GetSelection()].insert_grid(filename)

    def delete_grid(self, id_):
        """Delete a linked grid
        """
        self.__ca_list[self.GetSelection()].delete_grid(id_)

    def check_unredo(self):
        """Disables or enables undo and redo
        """
        ac_len, ac_ind = self.__ca_list[self.GetSelection()].actions_status()
        # DEBUG
        #debug("check_unredo", ("len", ac_len), ("index", ac_ind))
        if ac_ind == 0:
            self.__parent.DisableUndo()
        else:
            self.__parent.EnableUndo()
        if ac_len == ac_ind + 1:
            self.__parent.DisableRedo()
        else:
            self.__parent.EnableRedo()

    def _update_selection(self):
        """Update the current selection
        """
        self.__ca_list[self.GetSelection()].clear_selection()
        selected_cels = self.__renderer_list[
            self.GetSelection()].GetSelection()
        self.__ca_list[self.GetSelection()].select_entities(selected_cels)

    def undo(self):
        """Undo the last action
        """
        self.__ca_list[self.GetSelection()].undo()
        # DEBUG
        #debug("undo update selection")
        self._update_selection()
        self.check_unredo()

    def redo(self):
        """Redo the previous action
        """
        self.__ca_list[self.GetSelection()].redo()
        self._update_selection()
        self.check_unredo()

    def minimap(self):
        """Toggles minimap for all grids
        """
        for renderer in self.__renderer_list:
            renderer.toggle_minimap()

    def chess(self):
        """Toggles chess for all grids
        """
        for renderer in self.__renderer_list:
            renderer.toggle_chess()

    def smart_sel(self):
        """Enables or disables smart selection
        """
        self.__smart_selection = not self.__smart_selection
        if self.__smart_selection:
            StatusBarManager().UpdateStatusBar(
                None, "Smart selection activated")
        else:
            StatusBarManager().UpdateStatusBar(
                None, "Smart selection not active")

    def smart(self):
        """Return the status for smart selection
        """
        return self.__smart_selection

    def cut(self):
        """Cuts some entities from the current grid
        """
        self.__clipboard = dict()
        for pos, type_ in self.__ca_list[self.GetSelection()].get_entities_to_copy():
            self.__clipboard[pos] = type_
            self.__ca_list[self.GetSelection()].delete(pos)
        self.__clipboard_point = self.__renderer_list[
            self.GetSelection()].get_paste_pos()
        selected_cels = self.__renderer_list[
            self.GetSelection()].GetSelection()
        self.__ca_list[self.GetSelection()].select_entities(selected_cels)
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def copy(self):
        """Copies some entities from the current grid
        """
        self.__clipboard = dict()
        for pos, type_ in self.__ca_list[self.GetSelection()].get_entities_to_copy():
            self.__clipboard[pos] = type_
        self.__clipboard_point = self.__renderer_list[
            self.GetSelection()].get_paste_pos()
        #debug("copy", ("clipboard", self.__clipboard))

    def paste(self):
        """Pastes some entities from the clipboard to the current grid
        """
        l_x, l_y = self.__renderer_list[self.GetSelection()].get_paste_pos()
        p_x, p_y = self.__clipboard_point
        dif_x, dif_y = l_x - p_x, l_y - p_y
        for pos, type_ in self.__clipboard.viewitems():
            p_x, p_y = pos
            #debug("paste", ("pos", (p_x + dif_x, p_y + dif_y)), ("type", type_))
            self.__ca_list[self.GetSelection()].insert(
                Point(p_x + dif_x, p_y + dif_y), type_)
        selected_cels = self.__renderer_list[
            self.GetSelection()].GetSelection()
        self.__ca_list[self.GetSelection()].select_entities(selected_cels)
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def NewGrid(self):
        """Inserts a new tab with a new grid
        """
        self.__ca_list.append(CellularGrid(history=True))
        self.__ca_loop.append(False)
        self.__renderer_list.append(DrawWindow(self, fps=30.))
        if self.__parent.GetMinimapStatus():
            self.__renderer_list[-1].toggle_minimap()
        self.__renderer_list[-1].SetFocus()
        self.__renderer_list[-1].set_notebook(self)
        self.__files_names.append(None)
        self.AddPage(self.__renderer_list[-1], "Grid", select=True)

    def ClearLinks(self):
        """Deletes all links from the current grid
        """
        self.__ca_list[self.GetSelection()].clear_links()
        self.__gtree.UpdateTree()

    def Clear(self):
        """Delete everything on the current grid
        """
        self.__ca_list[self.GetSelection()].clear()
        self.__ca_list[self.GetSelection()].clear_links()
        self.__ca_list[self.GetSelection()].push_actions()
        self.__gtree.UpdateTree()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def ClearSparks(self):
        """Delete all sparks from the current grid
        """
        self.__ca_list[self.GetSelection()].clear_sparks()
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def Export(self):
        """Exports the current grid to a file
        """
        for x in range(0, len(self.__ca_loop)):
            self.__ca_loop[x] = False
        if len(self.__ca_list) != 0:
            files_types = "Grid Files (*.cg)|*.cg|File di Testo (*.txt)|*.txt|Tutti i Files (*)|*"
            dialog = wx.FileDialog(
                self, message="Salva come", defaultFile=".cg", wildcard=files_types, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )
            if dialog.ShowModal() == wx.ID_OK:
                file_path = dialog.GetPath()
                self.__ca_list[self.GetSelection()].store(file_path)
                self.__files_names[self.GetSelection()] = file_path
                self.SetPageText(self.GetSelection(), path.basename(file_path))
                self.__parent.set_title(
                    path.basename(file_path), path.dirname(file_path))
            dialog.Destroy()
            StatusBarManager().UpdateStatusBar("Grid exported!")

    def save_grid(self):
        """Saves the current grid
        """
        for x in range(0, len(self.__ca_loop)):
            self.__ca_loop[x] = False
        if len(self.__ca_list) != 0:
            if self.__files_names[self.GetSelection()] is None:
                self.Export()
            else:
                file_path = self.__files_names[self.GetSelection()]
                self.__ca_list[self.GetSelection()].store(file_path)
            StatusBarManager().UpdateStatusBar("Grid saved!")

    def Import(self):
        """Imports a grid from a file
        """
        for x in range(0, len(self.__ca_loop)):
            self.__ca_loop[x] = False
        if len(self.__ca_list) != 0:
            files_types = "Grid Files (*.cg)|*.cg|File di Testo (*.txt)|*.txt|Tutti i Files (*)|*"
            dialog = wx.FileDialog(
                self, message="Open grid file", wildcard=files_types, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
            if dialog.ShowModal() == wx.ID_OK:
                file_path = dialog.GetPath()
                self.__ca_list[self.GetSelection()].clear()
                self.__ca_list[self.GetSelection()].clear_links()
                self.__ca_list[self.GetSelection()].clear_selection()
                self.__ca_list[self.GetSelection()].load(file_path)
                self.__files_names[self.GetSelection()] = file_path
                self.SetPageText(self.GetSelection(), path.basename(file_path))
                self.__parent.set_title(
                    path.basename(file_path), path.dirname(file_path))
                # self.__renderer_list[self.GetSelection()].UpdateDrawing()
            dialog.Destroy()
            self.__ca_list[self.GetSelection()].push_actions()
            self.__gtree.UpdateTree()
            self.check_unredo()
            StatusBarManager().UpdateStatusBar("Grid imported!")

    def GetLastCellularGrid(self):
        """Returns the last grid inserted
        """
        return self.__ca_list[-1]

    def Insert(self, type_):
        """Insert an entity on the current grid
        """
        self.__renderer_list[self.GetSelection()].insert_entity(type_)
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def Rotate(self, deg):
        """Rotates some entities on the current grid
        """
        self._update_selection()
        self.__ca_list[self.GetSelection()].rotate(deg)
        self.__renderer_list[self.GetSelection()].rotate(deg)
        self._update_selection()
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def FlipH(self):
        """Flips horizonally some entities on the current grid
        """
        self._update_selection()
        self.__ca_list[self.GetSelection()].flip_h()
        self._update_selection()
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def FlipV(self):
        """Flips vertically some entities on the current grid
        """
        self._update_selection()
        self.__ca_list[self.GetSelection()].flip_v()
        self._update_selection()
        self.__ca_list[self.GetSelection()].push_actions()
        self.check_unredo()
        # self.__renderer_list[self.GetSelection()].UpdateDrawing()

    def PlayLoop(self, sel):
        """Continually updates the current grid if play button for this
        grid was pressed
        """
        # DEBUG
        #debug("RENDER LOOP", ("Selection", sel))
        if self.__ca_loop[sel]:
            self.__ca_list[sel].update()
            # self.__renderer_list[sel].UpdateDrawing()
            wx.CallLater(self.__delay, self.PlayLoop, sel)

    def Step(self):
        """Updates only one step for the current grid
        """
        self.__ca_list[self.GetSelection()].update()

    def LoopStart(self):
        """Returns the loop status for the current grid
        """
        return self.__ca_loop[self.GetSelection()]

    def Play(self):
        """Starts the play loop
        """
        # DEBUG
        #debug("PLAY", ("Selection", self.GetSelection()))
        self.__ca_loop[self.GetSelection()] = True
        # DEBUG
        #debug("PLAY COUNT", ("loop count", self.__ca_loop.count(True)))
        # if self.__ca_loop.count(True) == 1:
        self.PlayLoop(self.GetSelection())
        self.__parent.PlayOn()

    def Stop(self):
        """Stops the play loop
        """
        # DEBUG
        #debug("STOP", ("Count True", self.__ca_loop.count(True)))
        self.__ca_loop[self.GetSelection()] = False
        self.__parent.PlayOff()

    def StopAll(self):
        """Stop all loops of the grids and destroys contexts
        """
        # DEBUG
        #debug("BEFORE STOP")
        for x in range(0, len(self.__ca_loop)):
            self.__ca_loop[x] = False
        for x in range(0, len(self.__renderer_list)):
            self.__renderer_list[x].stop_timer()
            self.__renderer_list[x].Kill()
        # DEBUG
        #debug("AFTER STOP")

    def OnPageClose(self, event):
        """Close tab event
        """
        # DEBUG
        # debug("OnPageClose")
        selection = self.GetSelection()
        self.__ca_loop[selection] = False
        self.__ca_list.pop(selection)
        self.__files_names.pop(selection)
        self.__renderer_list.pop(selection)
        self.__ca_loop.pop(selection)
        event.Skip()

    def OnPageChanged(self, event):
        """Change tab event
        """
        # DEBUG
        # debug("OnPageChanged")
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # DEBUG
        #debug("OnPageChanged", ("old", old), ("new", new), ("sel", sel))
        self.__renderer_list[sel].SetFocus()
        self.__renderer_list[old].stop_timer()
        self.__renderer_list[sel].start_timer()
        if self.__files_names[sel] is not None:
            self.SetPageText(
                self.GetSelection(), path.basename(self.__files_names[sel]))
            self.__parent.set_title(
                path.basename(self.__files_names[sel]),
                path.dirname(self.__files_names[sel])
            )
        else:
            self.SetPageText(self.GetSelection(), "Grid")
            self.__parent.set_title()
        if self.__ca_loop[sel]:
            self.__parent.PlayOn()
        else:
            self.__parent.PlayOff()
        if self.__gtree:
            self.__gtree.UpdateTree()
        # DEBUG
        #debug("OnPageChanged",  ("old",old), ("new", new), ("sel", sel))
        event.Skip()

    def OnPageChanging(self, event):
        """Changing tab event
        """
        # DEBUG
        # debug("OnPageChanging")
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # DEBUG
        #debug("OnPageChanging",  ("old",old), ("new", new), ("sel", sel))
        event.Skip()

    def ProgramExit(self):
        """Function to exit from the whole program
        """
        self.__parent.OnExit()
