from __future__ import print_function
import wx
import pygame
from .utils import TS, rotate_point, debug, Point
from .ca_base_entity import ENTITIES_NAMES, ENTITIES_IDS
from .ca_link import LINK_TYPE_NAMES, LINK_TYPE_IDS
from .wxui_resman import ResourceManager
from .wxui_staman import StatusBarManager


class DrawWindow(wx.Window):
    """Class for grid rendering
    """
    def __init__(self, *args, **kwargs):
        kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN
        super(DrawWindow, self).__init__(*args, **kwargs)
        # Cellular Grid
        self.__cg = args[0].GetLastCellularGrid()
        # Mouse variables -----
        self.__show_ver_scrol = False
        self.__show_hor_scrol = False
        self.__selected_cels = list()
        self.__chess = True
        self.__start_selection = False
        self.__move_selection = False
        self.__lmp = Point(-1, -1) # last mouse position
        self.__pmp = Point(-1, -1) # previous mouse position
        self.__paste_pos = Point(-1, -1)
        self.__minimap = False
        # Other variables -----
        self.__link_selection = []
        self.__resman = ResourceManager() # Resource manager
        self.__notman = None # Notebook manager        
        self._size = self.GetSizeTuple() # Window size
        self._size_dirty = True
        self._screen = None
        # Device context for drawing the bitmap
        self._wx_dc = None
        # Timer -----
        self.timer = wx.Timer(self)
        self.fps = 30
        self.timespacing = 1000.0 / self.fps
        # Start timer -----
        self.timer.Start(self.timespacing, False)
        # Events binding -----
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind( wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind( wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind( wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.Bind( wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
    
    def on_cut(self):
        """Calls notebook cut method
        """
        self.__notman.cut()
    
    def on_copy(self):
        """Calls notebook copy method
        """
        self.__notman.copy()
    
    def on_paste(self):
        """Calls notebook paste method
        """
        self.__notman.paste()
    
    def set_link_selection(self, selection):
        """Update selected links
        """
        self.__link_selection = selection
    
    def start_timer(self):
        """Starts the timer
        """
        self.timer.Start(self.timespacing, False)
    
    def stop_timer(self):
        """Stops the timer
        """
        self.timer.Stop()
        
    def status_timer(self):
        """Return True if the timer is running
        """
        return self.timer.IsRunning()
    
    def toggle_minimap(self):
        """Toggle minimap status
        """
        self.__minimap = not self.__minimap
    
    def toggle_chess(self):
        """Toggle chess status
        """
        self.__chess = not self.__chess
    
    def set_notebook(self, notebook):
        """Set notebook reference
        """
        self.__notman = notebook
    
    def rotate_selection(self, deg):
        """Rotates the current selection
        """
        max_ = max(self.__selected_cels)
        min_ = min(self.__selected_cels)
        pivot = Point(
            min_[0] + ((max_[0] - min_[0]) / 2.),
            min_[1] + ((max_[1] - min_[1]) / 2.),
            )
        new_list = list()
        for point in self.__selected_cels:
            new_pos = rotate_point(point, pivot, deg)
            new_list.append(new_pos)
        return new_list
    
    def rotate(self, deg):
        """Check if the selection size and after rotates it
        """
        if len(self.__selected_cels) > 0:
            if self.__selection_size == (1, 1):
                return
            self.__selected_cels = self.rotate_selection(deg)
    
    def insert_entity(self, type_):
        """Insert an entity on the grid
        """
        # DEBUG
        #debug("insert_entity", ("type", type_))
        if len(self.__selected_cels) == 0:
            return
        min_ = min(self.__selected_cels)
        new_list = list()
        if self.__chess:
            row_odd = min_.x % 2 == 0
            column_odd =  min_.y % 2 == 0
            for point in self.__selected_cels:
                if (point.x % 2 == 0) == row_odd and\
                     (point.y % 2 == 0) == column_odd:
                    new_list.append(point)
        else:
            new_list = [point for point in self.__selected_cels]
        for sel in new_list:
            # DEBUG
            #debug("Insert Item", ("sel", sel), ("tipo", type_))
            if type_ in ENTITIES_NAMES:
                self.__cg.insert(sel, ENTITIES_NAMES[type_])
            if self.__link_selection is None or len(self.__link_selection) == 1:
                if type_ == "linkin":
                    self.__cg.insert_link(sel, LINK_TYPE_NAMES["IN"], True)
                elif type_ == "linkout":
                    self.__cg.insert_link(sel, LINK_TYPE_NAMES["OUT"], True)
            elif len(self.__link_selection) == 4:
                name, id_, pos, type_l = self.__link_selection
                if type_l == LINK_TYPE_NAMES["IN"] and type_ == "linkin":
                    self.__cg.insert_link(sel, LINK_TYPE_NAMES["IN"], False, id_, pos)
                elif type_l == LINK_TYPE_NAMES["OUT"] and type_ == "linkout":
                    self.__cg.insert_link(sel, LINK_TYPE_NAMES["OUT"], False, id_, pos)
        self.__cg.select_entities(self.__selected_cels)
        if self.__notman.smart():
            self.search_in_selection()
            self.update_selected_cels()
        self.__cg.select_entities(self.__selected_cels)
        if type_ != "linkin" and type_ != "linkout":
            self.__cg.push_actions()
        self.__notman.check_unredo()
    
    def get_paste_pos(self):
        """Get the position where to paste
        """
        return self.__paste_pos
    
    def update_selected_cels(self, min_=None, max_=None):
        """Update the mouse selection
        """
        if self.__pmp == (-1, -1):
            return
        list_ = list()
        # DEBUG
        #debug("update_selected_cels", ("oldlist", list_))
        #debug("update_selected_cels", ("first", max_), ("last", min_))
        x_f, y_f = self.__lmp if min_ is None else min_
        x_l, y_l = self.__pmp if max_ is None else max_
        if min_ is not None and max_ is not None:
            self.__lmp = (x_f, y_f)
            self.__pmp = (x_l, y_l)
        # DEBUG
        #debug("update_selected_cels", ("first", (x_f, y_f)), ("last", (x_l, y_l)))
        if x_f <= x_l and y_f <= y_l:
            self.__selection_size = (x_l - x_f + 1, y_l - y_f + 1)
            for x_c in range(x_f, x_l + 1):
                for y_c in range(y_f, y_l + 1):
                    list_.append(Point(x_c, y_c))
        elif x_f >= x_l and y_f >= y_l:
            self.__selection_size = (x_f - x_l + 1, y_f - y_l + 1)
            for x_c in range(x_l, x_f + 1):
                for y_c in range(y_l, y_f + 1):
                    list_.append(Point(x_c, y_c))
        elif x_f >= x_l and y_f <= y_l:
            self.__selection_size = (x_f - x_l + 1, y_l - y_f + 1)
            for x_c in range(x_l, x_f + 1):
                for y_c in range(y_f, y_l + 1):
                    list_.append(Point(x_c, y_c))
        elif x_f <= x_l and y_f >= y_l:
            self.__selection_size = (x_l - x_f + 1, y_f - y_l + 1)
            for x_c in range(x_f, x_l + 1):
                for y_c in range(y_l, y_f + 1):
                    list_.append(Point(x_c, y_c))
        # DEBUG
        #debug("update_selected_cels", ("newlist", list_))
        self.__paste_pos = min(list_)
        self.__selected_cels = list_
    
    def move_selection(self):
        """Move the mouse selection
        """
        diff_x = self.__pmp.x - self.__lmp.x
        diff_y = self.__pmp.y - self.__lmp.y
        new_list = list()
        self.__cg.move_selected_entities(diff_x, diff_y)
        for item in self.__selected_cels:
            i_x, i_y = item               
            new_list.append(Point(i_x - diff_x, i_y - diff_y))
        self.__selected_cels = new_list
        self.__pmp = self.__lmp
    
    def search_in_selection(self):
        """Search entities on the current selection
        """
        items_points = self.__cg.get_selection_entities_points()
        first = last = None
        if len(items_points) > 0:
            max_x = max([point[0] for point in items_points])
            max_y = max([point[1] for point in items_points])
            min_x = min([point[0] for point in items_points])
            min_y = min([point[1] for point in items_points])
            first = (max_x, max_y)
            last = (min_x, min_y)
        # DEBUG
        #debug("search_in_selection", ("first", first), ("last", last))
        self.update_selected_cels(last, first)
    
    ##
    # Events section ----------------------------------------------------------
    def OnMouseWheel(self, event):
        """Mouse wheel event
        """
        move = event.GetWheelRotation()/event.GetWheelDelta()
        pox_x, pos_y = event.GetPositionTuple()
        win_x, win_y = self._size
        if pox_x >= win_x - 25 and pox_x <= win_x and\
            pos_y >= 0 and pos_y <= win_y - 16:
            # Vertical scroll
            self.__cg.move_all(0, -move)
        elif pox_x >= 0 and pox_x <= win_x - 16 and\
            pos_y >= win_y - 25 and pos_y <= win_y:
            # Horizontal scroll
            self.__cg.move_all(move, 0)

    def OnMouseMotion(self, event):
        """Mouse motion event
        """
        position = event.GetPositionTuple()
        win_x, win_y = self._size
        if position[0] >= win_x - 16 and position[0] <= win_x and\
            position[1] >= 0 and position[1] <= win_y - 16:
            self.__show_ver_scrol = True
        else:
            self.__show_ver_scrol = False
        if position[0] >= 0 and position[0] <= win_x - 16 and\
            position[1] >= win_y - 16 and position[1] <= win_y:
            self.__show_hor_scrol = True
        else:
            self.__show_hor_scrol = False
        position = Point(position[0] / TS, position[1]/ TS)
        StatusBarManager().UpdateStatusBar(
            "Mouse in position: " + str(self.__lmp) +
            " | move: " + str(self.__move_selection) +
            " | selection: " + str(self.__start_selection))
        self.__lmp = position
        if self.__start_selection and not self.__move_selection:
            self.update_selected_cels()
        elif self.__move_selection:
            if self.__notman.LoopStart:
                self.__notman.Stop()
            self.move_selection()
        if not self.__notman.LoopStart():
            pass

    def OnMouseRightUp(self, event):
        """Mouse right button event (UP)
        """
        if self.__lmp in self.__selected_cels:
            self.__selected_cels = list()
        #self.UpdateDrawing()

    def OnMouseLeftUp(self, event):
        """Mouse left button event (UP)
        """
        self.__cg.select_entities(self.__selected_cels)
        self.__start_selection = False
        if self.__notman.smart():
            self.search_in_selection()
            self.update_selected_cels()
            self.__cg.select_entities(self.__selected_cels)
        if self.__move_selection:
            self.__cg.store_selection()
            self.__cg.push_actions()
            self.__notman.check_unredo()
        self.__move_selection = False
        #self.UpdateDrawing()

    def OnMouseLeftDown(self, event):
        """Mouse left button event (DOWN)
        """
        self.SetFocus()
        self.__pmp = self.__lmp
        if self.__lmp in self.__selected_cels:
            if self.__notman.LoopStart:
                self.__notman.Stop()
            self.__move_selection = True
            self.__cg.load_selection()
            self.move_selection()
        else:
            self.__start_selection = True
            self.update_selected_cels()
            self.__cg.clear_selection()
            #self.UpdateDrawing()

    def OnKeyDown(self, e):
        """Keyboard's events
        """
        # DEBUG
        #debug("keydown")
        key = e.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            ret  = wx.MessageBox('Are you sure to quit?', 'Question', 
                wx.YES_NO | wx.NO_DEFAULT, self) 
            if ret == wx.YES:
                self.__notman.ProgramExit()
        elif e.CmdDown() and key == ord("X"):
            self.on_cut()
        elif e.CmdDown() and key == ord("C"):
            self.on_copy()
        elif e.CmdDown() and key == ord("V"):
            self.on_paste()
        elif e.CmdDown() and key == ord("Z"):
            self.__notman.undo()
        elif key == ord("W"):
            self.insert_entity("arrowup")
        elif key == ord("A"):
            self.insert_entity("arrowleft")
        elif key == ord("D"):
            self.insert_entity("arrowright")
        elif key == ord("X"):
            self.insert_entity("arrowdown")
        elif key == ord("S"):
            self.insert_entity("spark")
        elif key == ord("I"):
            self.insert_entity("linkin")
        elif key == ord("O"):
            self.insert_entity("linkout")
        elif key == ord("C"):
            self.insert_entity("livingcell")
        elif key == ord("M"):
            self.insert_entity("monoone")
        elif key == wx.WXK_SPACE:
            self.__cg.update()
        elif key == wx.WXK_UP:
            self.__cg.move_all(0, -1)
        elif key == wx.WXK_DOWN:
            self.__cg.move_all(0, 1)
        elif key == wx.WXK_RIGHT:
            self.__cg.move_all(1, 0)
        elif key == wx.WXK_LEFT:
            self.__cg.move_all(-1, 0)
        elif key ==wx.WXK_DELETE:
            self.__cg.delete_selected_entities(links=True)
            if self.__cg.delete_selected_entities():
                self.__cg.push_actions()
            self.__notman.check_unredo()

    def GetSelection(self):
        """Returns the current selection
        """
        return self.__selected_cels
    
    def Update(self, event):
        """Draws all on the grid
        """
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def OnPaint(self, event):
        """Event OnPaint
        """
        self._wx_dc = wx.ClientDC(self)
        self.Redraw()
        event.Skip()  # Make sure the parent frame gets told to redraw as well
 
    def OnSize(self, event):
        """Event OnSize
        """
        self._size = self.GetSizeTuple()
        # DEBUG
        #debug("OnSize", ("Size", self._size))
        self._size_dirty = True
 
    def Kill(self):
        """Unbinding all methods whichcall the Redraw()
        """
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        # This may or may not be necessary now that Pygame is just drawing to surfaces
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
        del self._wx_dc
    
    ##
    # Support functions for drawing
    def __add_on_minimap(self, win_x, win_y, x_c, y_c, list_):
        if x_c >= -(win_x/TS) and x_c <= (win_x/TS)*2 and\
            y_c >= -(win_y/TS) and y_c <= (win_y/TS)*2:
            list_.append(Point((win_x / TS) + x_c, win_y - (win_y / TS)*2 + y_c))
    ##
    # Function that draws all entities on screen with pygame ------------------
    def Redraw(self):
        """Method called to draw
        """
        if self._size_dirty:
            self._screen = pygame.Surface(self._size, 0, 24)
            self._size_dirty = False
        
        win_x, win_y = self._size
        # Clear the screen -----
        for x in range(0, win_x / 512 + 2):
            for y in range(0, win_y / 512 + 2):
                self._screen.blit(self.__resman.entity.background, (x*512, y*512))  

        # Draw selection -----
        if len(self.__selected_cels) != 0:
            max_x, max_y = max(self.__selected_cels)
            min_x, min_y = min(self.__selected_cels)
            pygame.draw.rect(self._screen, (5,5,5), [min_x*TS, min_y*TS, (max_x - min_x + 1) * TS, (max_y - min_y + 1) * TS], 2)
        
        # Draw lines -----
        for x_c in range(0, win_x / TS + 1):
            pygame.draw.line(self._screen, (100,100,100), (x_c*TS, 0), (x_c*TS, win_y), 1)
        for y_c in range(0, win_y / TS + 1):
            pygame.draw.line(self._screen, (100,100,100), (0, y_c*TS), (win_x, y_c*TS), 1)
        
        if self.__minimap:
            points = list()
        
        # Draw my_links -----
        for pos, type_ in self.__cg.get_my_links():
            # DEBUG
            #debug("links", ("stat", (pos, type_)))
            x_c, y_c = pos
            if self.__minimap:
                self.__add_on_minimap(win_x, win_y, x_c, y_c, points)
            x_c, y_c = x_c*TS, y_c*TS
            if x_c >= 0 and x_c < win_x and \
                y_c >= 0 and y_c < win_y:
                try:
                    if len(self.__link_selection) == 1: # Same id of the selection
                        pygame.draw.rect(self._screen, self.__link_selection[0], [x_c, y_c, TS, TS], 1)
                except TypeError: # on deleting links it can return wx.Colour(-1, -1, -1, 255)
                    pass
                if type_ == LINK_TYPE_NAMES["IN"]:
                    self._screen.blit(self.__resman.tool.linkin, (x_c, y_c))
                elif type_ == LINK_TYPE_NAMES["OUT"]:
                    self._screen.blit(self.__resman.tool.linkout, (x_c, y_c))
        
        # Draw links -----
        for pos, type_, id_, id_pos in self.__cg.get_links():
            # DEBUG
            #debug("links", ("stat", (pos, type_, id_)))
            x_c, y_c = pos
            if self.__minimap:
                self.__add_on_minimap(win_x, win_y, x_c, y_c, points)
            x_c, y_c = x_c*TS, y_c*TS
            if x_c >= 0 and x_c < win_x and \
                y_c >= 0 and y_c < win_y:
                try:
                    if len(self.__link_selection) == 2\
                        and id_ == self.__link_selection[1]: # Same id of the selection
                        pygame.draw.rect(self._screen, self.__link_selection[0], [x_c, y_c, TS, TS], 1)
                    elif len(self.__link_selection) == 4\
                        and id_ == self.__link_selection[1]\
                         and type_ == self.__link_selection[3]\
                          and id_pos == self.__link_selection[2]:
                        pygame.draw.rect(self._screen, self.__link_selection[0], [x_c, y_c, TS, TS], 1)
                except TypeError: # on deleting links it can return wx.Colour(-1, -1, -1, 255)
                    pass
                if type_ == LINK_TYPE_NAMES["IN"]:
                    self._screen.blit(self.__resman.tool.linkin, (x_c, y_c))
                elif type_ == LINK_TYPE_NAMES["OUT"]:
                    self._screen.blit(self.__resman.tool.linkout, (x_c, y_c))
        
        # Draw entities -----
        for position, entity in self.__cg.get_entities():
            #debug("FOR", ("entity", entity), ("position", position))
            x_c, y_c = position
            if self.__minimap and ENTITIES_IDS[entity] in self.__resman.entity:
                self.__add_on_minimap(win_x, win_y, x_c, y_c, points)
            x_c, y_c = x_c*TS, y_c*TS
            if x_c >= 0 and x_c < win_x and \
                y_c >= 0 and y_c < win_y:
                # DEBUG
                #debug("Draw", ("position", (x_c, y_c)))
                if ENTITIES_IDS[entity] in self.__resman.entity:
                    self._screen.blit(self.__resman.entity[ENTITIES_IDS[entity]], (x_c, y_c))

        # Draw scrollbars -----
        if self.__show_hor_scrol:
            self._screen.fill((221, 221, 223), [0, win_y - 16, win_x, win_y])
            self._screen.blit(self.__resman.entity.arrowright, (win_x - 16, win_y - 16))
            self._screen.blit(self.__resman.entity.arrowleft, (0, win_y - 16))
        if self.__show_ver_scrol:
            self._screen.fill((221, 221, 223), [win_x - 16, 0, win_x, win_y])
            self._screen.blit(self.__resman.entity.arrowup, (win_x - 16, 0))
            self._screen.blit(self.__resman.entity.arrowdown, (win_x - 16, win_y - 16))
        ##
        # Minimap
        #  ________________________
        # |                        |
        # |        ________        |
        # |       |        |       |
        # |       |        |       |
        # |       |________|       |
        # |                        |
        # |________________________|
        #
        # top left corner = (0, win_y - (win_y / TS)*3)
        # width = ((win_x / TS)*3, (win_y / TS)*3)
        #
        # top left corner of inner box = ((win_x / TS), win_y - (win_y / TS)*2)
        # width inner box = (win_x / TS, win_y / TS)
        #
        # scale = 1 cell : 1 pixel on minimap
        #
        #--
        if self.__minimap:
            # External map
            
            pygame.draw.rect(self._screen, (75,75,75),
                [0, win_y - (win_y / TS)*3, (win_x / TS)*3, (win_y / TS)*3],
                3)
            self._screen.fill((255,255,255), [0, win_y - (win_y / TS)*3, (win_x / TS)*3, (win_y / TS)*3])
            # Map view
            pygame.draw.rect(self._screen, (75,75,75),
                [(win_x / TS), win_y - (win_y / TS)*2, win_x / TS, win_y / TS],
                3)
            self._screen.fill((255,255,255), [(win_x / TS), win_y - (win_y / TS)*2, win_x / TS, win_y / TS])
            for p in points:
                pygame.draw.rect(self._screen, (75,75,75),
                [p.x, p.y, 1, 1],
                1)

        # Convert the surface to an RGB string
        temp_s = pygame.image.tostring(self._screen, 'RGB')
        # Load this string into a wx image
        img = wx.ImageFromData(self._size[0], self._size[1], temp_s)
        # Get the image in bitmap form because
        # we can't render an image directly on context
        bmp = wx.BitmapFromImage(img)
        # Blit the bitmap image to the display
        self._wx_dc.DrawBitmap(bmp, 0, 0, False)