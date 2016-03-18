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
        super(MyGLCanvas, self).__init__(parent)

        self._env_type = kwargs.get('glenv', GLENV.env2d)
        self._gl_context = GLContext(self)
        self._gl_initialized = False
        self._wx_size = wx.Size(42, 42)
        self._size_t = self.GetSizeTuple()
        self._textures = {}

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self._init_GL()

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
        # Alpha
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glAlphaFunc(gl.GL_GREATER, 0)

    def _set_viewport(self):
        """Set viewport size as Client dimension."""
        self._wx_size = self.GetSize()
        self._size_t = self.GetSizeTuple()
        self.SetCurrent(self._gl_context)
        gl.glViewport(0, 0, self._wx_size.width, self._wx_size.height)
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

    def check_texture(self, name):
        return name in self._textures

    def add_texture(self, image, name=None,
                    t_wrap_s=gl.GL_REPEAT,
                    t_wrap_t=gl.GL_REPEAT,
                    t_mag_filter=gl.GL_LINEAR,
                    t_min_filter=gl.GL_LINEAR):
        """Add a texture to context.

        Params:
            image (object): an image object like wx.Image or Image from PIL
            name (string, default=None): name for the current texture
            t_wrap_s (GL constant,
                      default=GL_REPEAT): texture wrap s
            t_wrap_t (GL constant,
                      default=GL_REPEAT): texture wrap t
            t_mag_filter (GL constant,
                          default=GL_LINEAR): texture mag filter 
            t_min_filter (GL constant,
                          default=GL_LINEAR): texture min filter

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

    def draw_image(self, name, x, y, width, height):
        """Draw texture image on context.

        Params:
            name (string): string name of the texture
            x (int or float): x origin coordinates
            y (int or float): y origin coordinates
            width (int or float): desired width
            height (int or float): desired height
        """
        # Enable TEXTURE_2D
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._textures[name])

        # !!! Important !!!
        # -> Set current color
        # -->(similar to luminosity for current texture)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)

        # Enable BLEND
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Begin QUAD
        gl.glBegin(gl.GL_QUADS)

        gl.glTexCoord2f(0, 0)
        gl.glVertex2f(x, y)

        gl.glTexCoord2f(1, 0)
        gl.glVertex2f(x+width, y)

        gl.glTexCoord2f(1, 1)
        gl.glVertex2f(x+width, y+height)

        gl.glTexCoord2f(0, 1)
        gl.glVertex2f(x, y+height)

        gl.glEnd()
        gl.glDisable(gl.GL_BLEND)
        gl.glDisable(gl.GL_TEXTURE_2D)

    def draw_rect(self, x, y, width, height, color=(1.0, 1.0, 1.0, 1.0)):
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

    def draw(self):
        """Abstract method to draw on the canvas.

        Example of code:

        def draw(self):
            self.SetCurrent(self._gl_context)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glLoadIdentity()
            ...
            ...
            ...
            self.SwapBuffers()

        """
        raise NotImplementedError
