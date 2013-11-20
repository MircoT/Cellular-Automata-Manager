from __future__ import print_function, unicode_literals
import wx
import pygame
import logging
from wx.html import HtmlHelpController
from sys import exit, argv
from .utils import debug, __version__
from .wxui_resman import ResourceManager
from .wxui_staman import StatusBarManager
from .wxui_notebook import GridNotebook
from .wxui_treectrl import GridTreeCtrl


class App(wx.App):
    """
    Class for the Cellular Automata application
    """
    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super(App, self).__init__(redirect, filename, useBestVisual, clearSigInt)
        
    def OnInit(self):
        """Initialize the program
        """
        ResourceManager()
        self._editor = EditorFrame()
        self.SetExitOnFrameDelete(True)
        return True


class EditorFrame(wx.Frame):
    """
    Classe for the frame editor
    """
    def __init__(self):
        """Initialize the frame
        """
        # make sure the NO_FULL_REPAINT_ON_RESIZE style flag is set.
        self.__APP_NAME = "Cellular Automata Manager"
        super(EditorFrame,self).__init__(None, -1, self.__APP_NAME, style=wx.CENTER|wx.DEFAULT_FRAME_STYLE)
        self.__resman = ResourceManager()
        self.SetIcon(self.__resman.icon.cae)
        
        self.__linkers_ctrl = False
        self.__smart = False
        self.__minimap = False
        self.__chess = True
        self.__help = None
        
        self.__IDs = {
            'ID_NEW': wx.NewId(),
            'ID_CLEAR': wx.NewId(),
            'ID_CLEARSPARKS': wx.NewId(),
            'ID_CLEARLINKS': wx.NewId(),
            'ID_EXPORT': wx.NewId(),
            'ID_IMPORT': wx.NewId(),
            'ID_SAVE': wx.NewId(),
            'ID_CUT': wx.NewId(),
            'ID_COPY': wx.NewId(),
            'ID_PASTE': wx.NewId(),
            'ID_SMART_SEL': wx.NewId(),
            'ID_MINIMAP': wx.NewId(),
            'ID_CHESS': wx.NewId(),
            'ID_PLAY': wx.NewId(),
            'ID_STEP': wx.NewId(),
            'ID_STOP': wx.NewId(),
            'ID_UNDO': wx.NewId(),
            'ID_REDO': wx.NewId(),
            'ID_FLIP_H': wx.NewId(),
            'ID_FLIP_V': wx.NewId(),
            'ID_ROT_90': wx.NewId(),
            'ID_ROT_180': wx.NewId(),
            'ID_ROT_270': wx.NewId(),
            'ID_LINKIN': wx.NewId(),
            'ID_LINKOUT': wx.NewId(),
            'ID_LINK': wx.NewId(),
            'ID_SPARK': wx.NewId(),
            'ID_A_UP': wx.NewId(),
            'ID_A_DOWN': wx.NewId(),
            'ID_A_LEFT': wx.NewId(),
            'ID_A_RIGHT': wx.NewId(),
            'ID_AUTOMATA1D': wx.NewId()
        }

        #menu & toolbar
        self._SetupMenus()
        self._SetupToolBar()
        
        # Initialize checkitems
        self._menubar.Check(self.__IDs['ID_CHESS'], self.__chess)
        self._tb1.ToggleTool(self.__IDs['ID_CHESS'], self.__chess)
        self._tb1.EnableTool(self.__IDs['ID_REDO'], False)
        self._tb1.EnableTool(self.__IDs['ID_UNDO'], False)

        # notebook & gridtree
        self._notebook = GridNotebook(
            self, wx.ID_ANY,
            style=wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS | wx.aui.AUI_NB_MIDDLE_CLICK_CLOSE)
        self._tree_ctrl = GridTreeCtrl(parent=self)
        # set notebook & gridtree links
        self._tree_ctrl.SetNotebook(self._notebook)
        self._notebook.SetGridTree(self._tree_ctrl)

        s = wx.BoxSizer(wx.VERTICAL)

        s.Add(self._tb1, 0, wx.EXPAND)
        s.Add(self._tb2, 0, wx.EXPAND)
        s.Add(self._notebook, 1, wx.EXPAND)

        self.SetSizer(s)
        self.SetMinSize((800,600))
        self.SetSize((800,600))

        self.selection = False
        self.selected_tiles = list()

        self.__statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        StatusBarManager(self.__statusbar)

        # statusbar fields
        StatusBarManager().UpdateStatusBar("Init Statusbar", "Smart selection not active")
        # Events -----
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout,id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp,id=wx.ID_HELP)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TOOL, self.NewGrid, id=self.__IDs['ID_NEW'])
        self.Bind(wx.EVT_TOOL, self.ClearGrid, id=self.__IDs['ID_CLEAR'])
        self.Bind(wx.EVT_TOOL, self.ClearGridSparks, id=self.__IDs['ID_CLEARSPARKS'])
        self.Bind(wx.EVT_TOOL, self.ClearGridLinks, id=self.__IDs['ID_CLEARLINKS'])
        self.Bind(wx.EVT_TOOL, self.Export, id=self.__IDs['ID_EXPORT'])
        self.Bind(wx.EVT_TOOL, self.Import, id=self.__IDs['ID_IMPORT'])
        self.Bind(wx.EVT_TOOL, self.SaveGrid, id=self.__IDs['ID_SAVE'])
        self.Bind(wx.EVT_TOOL, self.Cut, id=self.__IDs['ID_CUT'])
        self.Bind(wx.EVT_TOOL, self.Copy, id=self.__IDs['ID_COPY'])
        self.Bind(wx.EVT_TOOL, self.Paste, id=self.__IDs['ID_PASTE'])
        self.Bind(wx.EVT_TOOL, self.SmartSel, id=self.__IDs['ID_SMART_SEL'])
        self.Bind(wx.EVT_TOOL, self.Minimap, id=self.__IDs['ID_MINIMAP'])
        self.Bind(wx.EVT_TOOL, self.Chess, id=self.__IDs['ID_CHESS'])
        self.Bind(wx.EVT_TOOL, self.Play, id=self.__IDs['ID_PLAY'])
        self.Bind(wx.EVT_TOOL, self.Stop, id=self.__IDs['ID_STOP'])
        self.Bind(wx.EVT_TOOL, self.Step, id=self.__IDs['ID_STEP'])
        self.Bind(wx.EVT_TOOL, self.Undo, id=self.__IDs['ID_UNDO'])
        self.Bind(wx.EVT_TOOL, self.Redo, id=self.__IDs['ID_REDO'])
        self.Bind(wx.EVT_TOOL, self.FlipH, id=self.__IDs['ID_FLIP_H'])
        self.Bind(wx.EVT_TOOL, self.FlipV, id=self.__IDs['ID_FLIP_V'])
        self.Bind(wx.EVT_TOOL, self.Rotate90, id=self.__IDs['ID_ROT_90'])
        self.Bind(wx.EVT_TOOL, self.Rotate180, id=self.__IDs['ID_ROT_180'])
        self.Bind(wx.EVT_TOOL, self.Rotate270, id=self.__IDs['ID_ROT_270'])
        self.Bind(wx.EVT_TOOL, self.Linkers, id=self.__IDs['ID_LINK'])
        self.Bind(wx.EVT_TOOL, self.InsertLinkin, id=self.__IDs['ID_LINKIN'])
        self.Bind(wx.EVT_TOOL, self.InsertLinkout, id=self.__IDs['ID_LINKOUT'])
        self.Bind(wx.EVT_TOOL, self.InsertSpark, id=self.__IDs['ID_SPARK'])
        self.Bind(wx.EVT_TOOL, self.InsertAUP, id=self.__IDs['ID_A_UP'])
        self.Bind(wx.EVT_TOOL, self.InsertADOWN, id=self.__IDs['ID_A_DOWN'])
        self.Bind(wx.EVT_TOOL, self.InsertARIGHT, id=self.__IDs['ID_A_RIGHT'])
        self.Bind(wx.EVT_TOOL, self.InsertALEFT, id=self.__IDs['ID_A_LEFT'])
        self.Bind(wx.EVT_TOOL, self.InsertAutomata1d, id=self.__IDs['ID_AUTOMATA1D'])
        
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Show()
    
    def SaveGrid(self, e):
        self._notebook.save_grid()
    
    
    def set_title(self, file_n=None, dir_n=None):
        """Set window title
        """
        if file_n is not None and dir_n is not None:
            self.SetTitle("%s (%s) - %s" % (file_n, dir_n, self.__APP_NAME))
        else:
            self.SetTitle(self.__APP_NAME)
    
    def Linkers(self, e):
        """Manage the visualization of the links manager
        """
        # DEBUG
        #debug("Linkers", ("__linkers_ctrl", self.__linkers_ctrl))
        self.__linkers_ctrl = not self.__linkers_ctrl
        self._menubar.Check(self.__IDs['ID_LINK'], self.__linkers_ctrl)
        self._tb2.ToggleTool(self.__IDs['ID_LINK'], self.__linkers_ctrl)
        if self.__linkers_ctrl:
            self._tree_ctrl.Show()
        else:
            self._tree_ctrl.Hide()
    
    def GetMinimapStatus(self):
        """Return the flag status for minimap button
        """
        return self._tb1.GetToolState(self.__IDs['ID_MINIMAP'])
    
    def EnableRedo(self):
        """Enable redo button
        """
        self._tb1.EnableTool(self.__IDs['ID_REDO'], True)
    
    def DisableRedo(self):
        """Disable redo button
        """
        self._tb1.EnableTool(self.__IDs['ID_REDO'], False)
        
    def EnableUndo(self):
        """Enable undo button
        """
        self._tb1.EnableTool(self.__IDs['ID_UNDO'], True)
    
    def DisableUndo(self):
        """Disable undo button
        """
        self._tb1.EnableTool(self.__IDs['ID_UNDO'], False)
    
    def PlayOn(self):
        """Set play button to True
        """
        self._tb1.ToggleTool(self.__IDs['ID_PLAY'], True)
    
    def PlayOff(self):
        """Set play button to False
        """
        self._tb1.ToggleTool(self.__IDs['ID_PLAY'], False)
    
    def Undo(self, e):
        """Undo last action
        
        Calls Notebook
        """
        self._notebook.undo()
    
    def Redo(self, e):
        """Redo previous action
        
        Calls Notebook
        """
        self._notebook.redo()
    
    def Minimap(self, e):
        """Toggle minimap
        
        Calls Notebook
        """
        self.__minimap = not self.__minimap
        self._menubar.Check(self.__IDs['ID_MINIMAP'], self.__minimap)
        self._tb1.ToggleTool(self.__IDs['ID_MINIMAP'], self.__minimap)
        self._notebook.minimap()
    
    def Chess(self, e):
        """Toggle chess insertion
        
        Calls Notebook
        """
        self.__chess = not self.__chess
        self._menubar.Check(self.__IDs['ID_CHESS'], self.__chess)
        self._tb1.ToggleTool(self.__IDs['ID_CHESS'], self.__chess)
        self._notebook.chess()

    def SmartSel(self, e):
        """Toggle smart selection
        
        Calls Notebook
        """
        self.__smart = not self.__smart
        self._menubar.Check(self.__IDs['ID_SMART_SEL'], self.__smart)
        self._tb1.ToggleTool(self.__IDs['ID_SMART_SEL'], self.__smart)
        self._notebook.smart_sel()
    
    def InsertLinkin(self, e):
        """Insert link in
        
        Calls Notebook
        """
        self._notebook.Insert("linkin")
    
    def InsertLinkout(self, e):
        """Insert link out
        
        Calls Notebook
        """
        self._notebook.Insert("linkout")
    
    def InsertSpark(self, e):
        """Insert sparks
        
        Calls Notebook
        """
        self._notebook.Insert("spark")
    
    def InsertAUP(self, e):
        """Insert up arrows
        
        Calls Notebook
        """
        self._notebook.Insert("arrowup")
    
    def InsertADOWN(self, e):
        """Insert down arrows
        
        Calls Notebook
        """
        self._notebook.Insert("arrowdown")
    
    def InsertARIGHT(self, e):
        """Insert right arrows
        
        Calls Notebook
        """
        self._notebook.Insert("arrowright")
    
    def InsertALEFT(self, e):
        """Insert left arrows
        
        Calls Notebook
        """
        self._notebook.Insert("arrowleft")
    
    def InsertAutomata1d(self, e):
        """Insert an entity for one dimension automata
        
        Calls Notebook
        """
        self._notebook.Insert("monoone")

    def Cut(self, e):
        """Cut entities from the grid and put them on the clipboard
        
        Calls Notebook
        """
        self._notebook.cut()
    
    def Copy(self, e):
        """Copy entities on the clipboard
        
        Calls Notebook
        """
        self._notebook.copy()
    
    def Paste(self, e):
        """Paste entities on the clipboard to the grid
        
        Calls Notebook
        """
        self._notebook.paste()
    
    def Export(self, e):
        """Export grid to a file
        
        Calls Notebook
        """
        self._notebook.Export()
    
    def Import(self, e):
        """Import grid from a file
        
        Calls Notebook
        """
        self._notebook.Import()
    
    def Rotate90(self, e):
        """Rotate entities by 90 degrees
        
        Calls Notebook
        """
        self._notebook.Rotate(90)
    
    def Rotate180(self, e):
        """Rotate entities by 180 degrees
        
        Calls Notebook
        """
        self._notebook.Rotate(180)
    
    def Rotate270(self, e):
        """Rotate entities by 270 degrees
        
        Calls Notebook
        """
        self._notebook.Rotate(270)
    
    def NewGrid(self, e):
        """Open a new tab with a new grid
        
        Calls Notebook
        """
        self._notebook.NewGrid()
    
    def ClearGrid(self, e):
        """Clear the grid
        
        Calls Notebook
        """
        self._notebook.Clear()
    
    def ClearGridSparks(self, e):
        """Delete all grid's sparks
        
        Calls Notebook
        """
        self._notebook.ClearSparks()
    
    def ClearGridLinks(self, e):
        """Delete all grid's links
        
        Calls Notebook
        """
        self._notebook.ClearLinks()
    
    def Play(self, e):
        """Start execution
        
        Calls Notebook
        """
        self._menubar.Check(self.__IDs['ID_PLAY'], True)
        self._tb1.ToggleTool(self.__IDs['ID_PLAY'], True)
        self._notebook.Play()
    
    def Stop(self, e):
        """Stop execution
        
        Calls Notebook
        """
        self._menubar.Check(self.__IDs['ID_PLAY'], False)
        self._tb1.ToggleTool(self.__IDs['ID_PLAY'], False)
        self._notebook.Stop()
    
    def Step(self, e):
        """Advanced by one step
        
        Calls Notebook
        """
        self._notebook.Step()
    
    def FlipH(self, e):
        """Flip entities horizontally
        
        Calls Notebook
        """
        self._notebook.FlipH()
    
    def FlipV(self, e):
        """Flip entities vertically
        
        Calls Notebook
        """
        self._notebook.FlipV()
    
    def OnKeyDown(self, e):
        e.Skip()

    def OnAbout(self,event):
        """
        Information dialog
        """
        info = wx.AboutDialogInfo()
        
        description = """Open source environment for cellular automata.
        """
        licenza = """Copyright (C) 2013 Mirco Tracolli

This program is free software: you can redistribute it and/or modify it underthe terms of
the GNU General Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see http://www.gnu.org/licenses/."""
        info.SetIcon(self.__resman.icon.cae)
        info.SetName("Cellular Automata Manager")
        info.SetVersion(__version__)
        info.SetDescription(description)
        info.SetCopyright("Copyright (C) 2013 Mirco Tracolli")
        info.SetWebSite("https://github.com/MircoT/Cellular-Automata-Manager")
        info.SetLicence(licenza)
        info.AddDeveloper("Mirco Tracolli")
        wx.AboutBox(info)
    
    def OnHelp(self,event):
        """
        Instruction dialog
        """
        if not self.__help:
            self.__help = HtmlHelpController()
            self.__help.AddBook("doc/doc.hhp")
        self.__help.DisplayContents()
    
    def _SetupToolBar(self):
        """Toolbars' setup
        """
        # First toolbar
        self._tb1 = wx.ToolBar(self, size=wx.DefaultSize)
        self._tb1.AddLabelTool(
            self.__IDs["ID_NEW"], "New", self.__resman.button.new,
            shortHelp="New", longHelp="Open an empy grid in a new tab"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_CLEAR"], "Clear", self.__resman.button.cleargrid,
            shortHelp="Clear", longHelp="Clear the grid in the current tab"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_CLEARSPARKS"], "Clear Sparks", self.__resman.button.clearsparks,
            shortHelp="Clear Sparks", longHelp="Delete all the sparks in the current grid opened"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_CLEARLINKS"], "Clear Links", self.__resman.button.clearlinks,
            shortHelp="Clear Links", longHelp="Delete all the links in the current grid opened"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_EXPORT"], "Export", self.__resman.button.exportgrid,
            shortHelp="Export", longHelp="Export the current grid to a file"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_IMPORT"], "Import", self.__resman.button.importgrid,
            shortHelp="Import", longHelp="Import a grid from a file"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_SAVE"], "Save", self.__resman.button.save,
            shortHelp="Save", longHelp="Save the current grid"
        )
        self._tb1.AddSeparator()
        self._tb1.AddLabelTool(
            self.__IDs["ID_CUT"], "Cut", self.__resman.button.cuten,
            shortHelp="Cut", longHelp="Cut some entities from the grid"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_COPY"], "Copy", self.__resman.button.copyen,
            shortHelp="Copy", longHelp="Copy some entities from the grid"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_PASTE"], "Paste", self.__resman.button.pasteen,
            shortHelp="Paste", longHelp="Paste entities from the clipboard"
        )
        self._tb1.AddSeparator()
        self._tb1.AddCheckLabelTool(
            self.__IDs["ID_SMART_SEL"], "Smart Selection", self.__resman.button.smartselection,
            shortHelp="Smart Selection", longHelp="Enable/disable smart selection"
        )
        self._tb1.AddCheckLabelTool(
            self.__IDs["ID_MINIMAP"], "Minimap", self.__resman.button.minimap,
            shortHelp="Minimap", longHelp="Enable/disable Minimap"
        )
        self._tb1.AddCheckLabelTool(
            self.__IDs["ID_CHESS"], "Chess", self.__resman.button.chess,
            shortHelp="Chess", longHelp="Enable/disable chess selection to create new entities"
        )
        self._tb1.AddSeparator()
        self._tb1.AddCheckLabelTool(
            self.__IDs["ID_PLAY"], "Play", self.__resman.button.play,
            shortHelp="Play", longHelp="Start simulation on the current grid"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_STEP"], "Step", self.__resman.button.step,
            shortHelp="Step", longHelp="Simulates only one step on the current grid"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_STOP"], "Stop", self.__resman.button.stop,
            shortHelp="Stop", longHelp="Stop the simulation on the current grid"
        )
        self._tb1.AddSeparator()
        self._tb1.AddLabelTool(
            self.__IDs["ID_UNDO"], "Undo", self.__resman.button.undo,
            shortHelp="Undo", longHelp="Undo latest action on the current grid"
        )
        self._tb1.AddLabelTool(
            self.__IDs["ID_REDO"], "Redo", self.__resman.button.redo,
            shortHelp="Redo", longHelp="Redo an action on the current grid"
        )       
        self._tb1.Realize()
        # Second toolbar
        self._tb2 = wx.ToolBar(self, size=wx.DefaultSize)
        self._tb2.AddLabelTool(
            self.__IDs["ID_FLIP_H"], "Horiziontal flip", self.__resman.button.fliph,
            shortHelp="Horiziontal flip", longHelp="Flip horizontally the selected entities"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_FLIP_V"], "Vertical flip", self.__resman.button.flipv,
            shortHelp="Vetical flip", longHelp="Flip vertically the selected entities"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_ROT_90"], "Rotate 90 deg", self.__resman.button.rot90,
            shortHelp="Rotate 90 deg", longHelp="Rotate by 90 degrees the selected entities"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_ROT_180"], "Rotate 180 deg", self.__resman.button.rot180,
            shortHelp="Rotate 180 deg", longHelp="Rotate by 180 degrees the selected entities"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_ROT_270"], "Rotate 270 deg", self.__resman.button.rot270,
            shortHelp="Rotate 270 deg", longHelp="Rotate by 270 degrees the selected entities"
        )
        self._tb2.AddSeparator()
        self._tb2.AddLabelTool(
            self.__IDs["ID_LINKIN"], "Link IN", self.__resman.button.linkin,
            shortHelp="Link IN", longHelp="Inserts a Link IN for the selected grid"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_LINKOUT"], "Link OUT", self.__resman.button.linkout,
            shortHelp="Link OUT", longHelp="Inserts a Link OUT for the selected grid"
        )
        self._tb2.AddCheckLabelTool(
            self.__IDs["ID_LINK"], "Linkers", self.__resman.button.linkers,
            shortHelp="Linkers", longHelp="Open the links manager"
        )
        self._tb2.AddSeparator()
        self._tb2.AddLabelTool(
            self.__IDs["ID_SPARK"], "Spark", self.__resman.button.spark,
            shortHelp="Spark", longHelp="Inserts a spark entity"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_A_UP"], "Arrow UP", self.__resman.button.arrowup,
            shortHelp="Arrow UP", longHelp="Inserts an arrow up entity"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_A_DOWN"], "Arrow DOWN", self.__resman.button.arrowdown,
            shortHelp="Arrow DOWN", longHelp="Inserts an arrow down entity"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_A_RIGHT"], "Arrow RIGHT", self.__resman.button.arrowright,
            shortHelp="Arrow RIGHT", longHelp="Inserts an arrow right entity"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_A_LEFT"], "Arrow LEFT", self.__resman.button.arrowleft,
            shortHelp="Arrow LEFT", longHelp="Inserts an arrow left entity"
        )
        self._tb2.AddLabelTool(
            self.__IDs["ID_AUTOMATA1D"], "1D Automata", self.__resman.button.automata1d,
            shortHelp="1D Automata", longHelp="Inserts an entity of a monodimensional automata"
        )
        self._tb2.Realize()
    
    def _SetupMenus(self):
        """Menues' setup
        """
        
        self._menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(self.__IDs['ID_NEW'], "New\tCtrl+N")
        menu.Append(self.__IDs['ID_IMPORT'], "Import\tCtrl+I")
        menu.AppendSeparator()
        menu.Append(self.__IDs['ID_CLEAR'],"Clear")
        menu.Append(self.__IDs['ID_CLEARSPARKS'],"Clear Sparks")
        menu.Append(self.__IDs['ID_CLEARLINKS'],"Clear Links")
        menu.AppendSeparator()
        menu.Append(self.__IDs['ID_EXPORT'], "Export\tCtrl+Shift+E")
        menu.Append(self.__IDs['ID_SAVE'], "Save\tCtrl+S")
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self._menubar.Append(menu, "Actions")
        
        edit = wx.Menu()
        edit.Append(self.__IDs['ID_UNDO'],"Undo")
        edit.Append(self.__IDs['ID_REDO'],"Redo")
        edit.AppendSeparator()
        edit.Append(self.__IDs['ID_CUT'],"Cut")
        edit.Append(self.__IDs['ID_COPY'],"Copy")
        edit.Append(self.__IDs['ID_PASTE'],"Paste")
        edit.AppendSeparator()
        edit.Append(self.__IDs['ID_FLIP_H'],"Flip horizontally")
        edit.Append(self.__IDs['ID_FLIP_V'],"Flip vertically")
        edit.Append(self.__IDs['ID_ROT_90'],"Rotate 90 deg")
        edit.Append(self.__IDs['ID_ROT_180'],"Rotate 180 deg")
        edit.Append(self.__IDs['ID_ROT_270'],"Rotate 270 deg")
        self._menubar.Append(edit, "Edit")
        
        environment = wx.Menu()
        environment.Append(self.__IDs["ID_SMART_SEL"],"Smart selection", kind=wx.ITEM_CHECK)
        environment.Append(self.__IDs["ID_MINIMAP"],"Minimap", kind=wx.ITEM_CHECK)
        environment.Append(self.__IDs["ID_CHESS"],"Chess creation", kind=wx.ITEM_CHECK)
        environment.AppendSeparator()
        environment.Append(self.__IDs["ID_PLAY"],"Play", kind=wx.ITEM_CHECK)
        environment.Append(self.__IDs["ID_STEP"],"Step")
        environment.Append(self.__IDs["ID_STOP"],"Stop")
        self._menubar.Append(environment, "Environment")
        
        items = wx.Menu()
        items.Append(self.__IDs["ID_SPARK"],"Spark")
        items.Append(self.__IDs["ID_A_UP"],"Arrow UP")
        items.Append(self.__IDs["ID_A_DOWN"],"Arrow DOWN")
        items.Append(self.__IDs["ID_A_RIGHT"],"Arrow RIGHT")
        items.Append(self.__IDs["ID_A_LEFT"],"Arrow LEFT")
        items.Append(self.__IDs["ID_AUTOMATA1D"],"1D Automata")
        items.AppendSeparator()
        items.Append(self.__IDs["ID_LINKIN"],"Link IN")
        items.Append(self.__IDs["ID_LINKOUT"],"Link OUT")
        items.Append(self.__IDs["ID_LINK"],"Links Manager", kind=wx.ITEM_CHECK)
        self._menubar.Append(items, "Items")
        
        info = wx.Menu()
        info.Append(wx.ID_ABOUT, "Cellular Automata Manager")
        info.Append(wx.ID_HELP, "Help")
        self._menubar.Append(info,"Info")
        
        self.SetMenuBar(self._menubar)
    
    def OnExit(self, event=None):
        """Exit from the program
        """
        self._notebook.StopAll()
        self.Destroy()

def main():
    if len(argv) == 1:
        my_app = App()
        my_app.MainLoop()
    elif len(argv) == 2 and argv[1] == "debug":
        logging.basicConfig(level=logging.DEBUG)
        debug("APP STARTED")
        my_app = App()
        my_app.MainLoop()
        debug("APP FINISHED")
    elif len(argv) == 3 and argv[1] == "debug" and argv[2] == "onfile":
        logging.basicConfig(filename='app.log', level=logging.DEBUG)
        debug("APP STARTED")
        my_app = App()
        my_app.MainLoop()
        debug("APP FINISHED")
    else:
        print("Command not recognized")
        return 1