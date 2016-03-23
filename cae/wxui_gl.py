#! *-* coding: utf-8 *-*
import wx
import OpenGL.GL as gl
from wx.glcanvas import GLCanvas, GLContext
from PIL import Image, PngImagePlugin, BmpImagePlugin
from collections import namedtuple

__all__ = ['MyGLCanvas', 'GLENV']

__ENVS = ['env2d', 'env3d']
__GL_ENVS = namedtuple('__GL_ENVS', __ENVS)
# Constants
GLENV = __GL_ENVS(*range(len(__ENVS)))


class MyGLCanvas(GLCanvas):

    """Class to manage an OpenGL canvas in wxPython."""

    def __init__(self, parent, *args, **kwargs):
        """Initialize the canvas.

        Params:
            parent (wx.Window): reference to parent
            glenv (GLENV): type of canvas generated
            fps (float): number of frame per second

        If fps is omitted the canvas will not have
        a timer that calls the function update for
        each frame.
        """
        super(MyGLCanvas, self).__init__(parent)

        self._env_type = kwargs.get('glenv', GLENV.env2d)
        self._gl_context = GLContext(self)
        self._gl_initialized = False
        self._wx_size = wx.Size(42, 42)
        self._size_t = self.GetSizeTuple()
        self._textures = {}

        self._fps = kwargs.get('fps', None)

        ##
        # Timer
        if self._fps is not None:
            self._timer = wx.Timer(self)
            self._timespacing = 1000.0 / self._fps
            # Timer binding
            self.Bind(wx.EVT_TIMER, self.update, self._timer)

            self._timer.Start(self._timespacing, False)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self._init_GL()

    def Kill(self):
        """Unbinding all methods whichcall the Redraw()
        """
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
        if self._timer is not None:
            self.Unbind(
                event=wx.EVT_TIMER, handler=self.update, source=self._timer)

    def start_timer(self):
        """Starts the timer."""
        self._timer.Start(self._timespacing, False)

    def stop_timer(self):
        """Stops the timer."""
        self._timer.Stop()

    def status_timer(self):
        """Return True if the timer is running."""
        return self._timer.IsRunning()

    def OnEraseBackground(self, event):
        """Manage background erase.

        Tip: do nothing, to avoid flashing on Windows OS
        """
        pass

    def OnSize(self, event):
        """Manage Viewport on resize window."""
        wx.CallAfter(self._set_viewport)
        event.Skip()

    def OnPaint(self, event):
        """Method that draw on the context."""
        # Draw contents
        self.draw()
        event.Skip()

    def _init_GL(self):
        """Initialize OpenGwidthL context."""
        self.SetCurrent(self._gl_context)
        self.def_clear_color(0.98, 0.98, 0.98, 1.0)
        if self._env_type == GLENV.env2d:
            self._conf_2d_env()
        else:
            raise Exception('3D context not yet implemented')
        self.SwapBuffers()

    def _conf_2d_env(self):
        """Configure the context for 2D environment."""
        gl.glViewport(0, 0, self._wx_size.width, self._wx_size.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0.0, self._wx_size.width,
                   0.0, self._wx_size.height,
                   0.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # Lines
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(1.0)

    def _set_viewport(self):
        """Set viewport size as Client dimension."""
        self._wx_size = self.GetSize()
        self._size_t = self.GetSizeTuple()
        self.SetCurrent(self._gl_context)
        self._conf_2d_env()

    def def_clear_color(self, r=0.0, g=0.0, b=0.0, a=1.0):
        """Change default color with which canvas is cleaned.

        Params:
            r (float): red value
            g (float): green value
            b (float): blue value
            a (float): alpha value
        """
        gl.glClearColor(r, g, b, a)

    def add_texture(self, image, name=None,
                    t_wrap_s=gl.GL_REPEAT,
                    t_wrap_t=gl.GL_REPEAT,
                    t_mag_filter=gl.GL_NEAREST,
                    t_min_filter=gl.GL_NEAREST):
        """Add a texture to context.

        Params:
            image (object): an image object like wx.Image or Image from PIL
            name (string, default=None): name for the current texture
            t_wrap_s (GL constant, default=GL_REPEAT): texture wrap s
            t_wrap_t (GL constant, default=GL_REPEAT): texture wrap t
            t_mag_filter (GL constant, default=GL_LINEAR): texture mag filter 
            t_min_filter (GL constant, default=GL_LINEAR): texture min filter

        Returns:
            name (string): name of the texture created. If no name
                           is passed during the creation a template
                           will be filled ('texture_{number}')

        Raises:
            Exception if image type is not supported or the kind
            of the image hasn't the implementation
        """
        img_type = None
        img_width = -1
        img_height = -1
        img_data = None

        # wx.Image
        if isinstance(image, wx.Image):
            img_type = gl.GL_RGB
            img_width = image.Width
            img_height = image.Height
            img_data = image.GetData()
        # Pillow image
        elif isinstance(image, PngImagePlugin.PngImageFile):
            if image.mode == 'RGB':
                img_type = gl.GL_RGB
            elif image.mode == 'RGBA':
                img_type = gl.GL_RGBA
            else:
                raise Exception(
                    "Image mode {0} not implemented for Pillow PNG".format(image.mode))
            img_width = image.width
            img_height = image.height
            img_data = image.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        # Pillow image
        elif isinstance(image, BmpImagePlugin.BmpImageFile):
            if image.mode == 'RGB':
                img_type = gl.GL_RGB
            else:
                raise Exception(
                    "Image mode {0} not implemented for Pillow Bitmap".format(image.mode))
            img_width = image.width
            img_height = image.height
            img_data = image.tobytes()
        else:
            raise Exception(
                "object {0} not supported... use wx.Image or Image from PIL".format(type(image)))

        texture = gl.glGenTextures(1)

        if name is None:
            name = "texture_{0}".format(texture)

        self._textures[name] = texture

        gl.glBindTexture(gl.GL_TEXTURE_2D, self._textures[name])
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, t_wrap_s)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, t_wrap_t)

        gl.glTexParameterf(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, t_mag_filter)
        gl.glTexParameterf(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, t_min_filter)

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, img_type,
                        img_width, img_height,
                        0, img_type, gl.GL_UNSIGNED_BYTE, img_data)

        return name

    def draw_image(self, name, x, y, angle=0.0, size=(64, 64), origin=(0.5, 0.5)):
        """Draw texture image on context.

        Params:
            name (string): string name of the texture
            x (int or float): x origin coordinates
            y (int or float): y origin coordinates
            angle (float, default=0.0): rotation angle
            size (tuple, default=(64, 64)): size of the image on the canvas
            origin (tuple, default=(0.5, 0.5)): start point of the renderer
        """
        # Enable TEXTURE_2D
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._textures[name])

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        ##
        # Transformations:
        # - Translate(Rotate(Scale()))
        gl.glTranslatef(
            x + size[0]*(0.5-origin[0]),
            y + size[1]*(0.5-origin[1]),
            0)
        gl.glRotatef(angle, 0, 0, 1)
        gl.glScale(size[0], size[1], 1.0)

        # !!! Important !!!
        # -> Set current color to render the image
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)

        # Enable BLEND
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Begin QUAD
        gl.glBegin(gl.GL_QUADS)

        """
        glTexCoord2 (x,y):

            (0, 1)   ___________________  (1, 1)
                    |                   |
                    |                   |
                    |     (0.5, 0.5)    |
                    |         .         |
                    |                   |
                    |                   |
                    |                   |
            (0, 0)   -------------------  (1, 0)

        glVertex2f (x,y):

                           │
             (-0.5, 0.5)   │   (0.5, 0.5)
                       *---│---*
                       │   │   │
                ───────────┼───────────
                       │   │   │
                       *---│---*
            (-0.5, -0.5)   │   (0.5, -0.5)
                           │

            From here will be applied:
            - Scale() -> Rotate() -> Translate()
        """

        gl.glTexCoord2f(0, 0)
        gl.glVertex2f(-0.5, -0.5)

        gl.glTexCoord2f(1, 0)
        gl.glVertex2f(0.5, -0.5)

        gl.glTexCoord2f(1, 1)
        gl.glVertex2f(0.5, 0.5)

        gl.glTexCoord2f(0, 1)
        gl.glVertex2f(-0.5, 0.5)

        gl.glEnd()
        gl.glDisable(gl.GL_BLEND)
        gl.glDisable(gl.GL_TEXTURE_2D)

    def draw_rect(self, x, y, width, height, color=(1.0, 1.0, 1.0, 1.0)):
        """Draw rect on canvas."""
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glColor4f(*color)

        # Begin QUAD
        gl.glBegin(gl.GL_QUADS)
        # bottom left point
        gl.glVertex2f(x, y)
        # bottom right point
        gl.glVertex2f(x + width, y)
        # top right point
        gl.glVertex2f(x + width, y + height)
        # top left point
        gl.glVertex2f(x, y + height)
        # End QUAD
        gl.glEnd()

    def draw_line(self, start_x, start_y, end_x, end_y,
                  color=(1.0, 1.0, 1.0, 1.0),
                  width=None):
        """Draw a line on canvas."""
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glColor4f(*color)

        prev_width = None
        if width is not None:
            prev_width = gl.glGetFloat(gl.GL_LINE_WIDTH)
            gl.glLineWidth(width)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_DONT_CARE)

        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(start_x, start_y)
        gl.glVertex2f(end_x, end_y)
        gl.glEnd()
        gl.glDisable(gl.GL_BLEND)

        if prev_width is not None:
            gl.glLineWidth(prev_width)

    def canvas_image(self, image_name,
                     size=(64.0, 64.0),
                     origin=(0.5, 0.5)):
        """Create an Image that can be draw on the canvas.

        Params:
            image_name (string): name of the image to open
            size (tuple, default=(64, 64)): size of the image on the canvas
            origin (tuple, default=(0.5, 0.5)): start point of the renderer

        Returns:
            CanvasImage object

        """
        return CanvasImage(self, image_name, size, origin)

    def update(self, event):
        """Update function for timer.

        This method will cal draw after a clear of the screen,
        like OnPaint method but used inside the timer to refresh
        the screen with a certain fps.
        """
        self.draw()
        event.Skip()

    def draw(self):
        """Abstract method to draw on the canvas."""
        raise NotImplementedError


class CanvasImage:

    """Class to manage images inside the canvas."""

    def __init__(self, canvas, image_name, size=(64, 64), origin=(0.5, 0.5)):
        """Constructor of the CanvasImage object.

        Params:
            canvas (MyGLCanvas): canvas with OpenGL context
            image_name (string): name of the image to open
            size (tuple, default=(64, 64)): size of the image on the canvas
            origin (tuple, default=(0, 0)): start point of the renderer
        """
        self._image = Image.open(image_name)
        self._texture_name = canvas.add_texture(self._image)
        self._size = size
        self._orgin = origin
        self._canvas = canvas

    def set_origin(self, x, y):
        """Change origin coordinates.

        Origin(x,y):

            (0, 1)   ___________________  (1, 1)
                    |                   |
                    |                   |
                    |     (0.5, 0.5)    |
                    |         .         |
                    |                   |
                    |                   |
                    |                   |
            (0, 0)   -------------------  (1, 0)

        """
        self._origin = (x, y)

    def set_size(self, width, height):
        """Change size of the image on the canvas."""
        self._size = (width, height)

    def draw(self, x, y, angle=0.0):
        """Draw the image on the canvas.

        Params:
            x (float): x coordinate on the canvas
            y (float): y coordinate on the canvas
            angle (float, default=0.0): rotation angle
        """
        self._canvas.draw_image(self._texture_name,
                                x, y, angle,
                                self._size,
                                self._orgin)
