import cv2
from OpenGL import GL
from PySide.QtCore import QRectF, Qt
from PySide.QtGui import QImage
from PySide.QtOpenGL import QGLWidget


class KeyFramePreview(QGLWidget):
    """QtGui.QWidget for KeyFrame visualisation:
        image + matched object projection
    """

    def __init__(self, _keyframe, _object, parent=None):
        QGLWidget.__init__(self, parent)
        self.frame = _keyframe
        self.object = _object

    def initializeGL(self):
        GL.glClearDepth(1.0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(1, 1)

        image = cv2.flip(self.frame.image, 0)
        height, width, channel = image.shape
        image = QImage(image.data, width, height, QImage.Format_RGB888)
        self.texture = self.bindTexture(image.rgbSwapped())

        self.objectDrawer = GL.glGenLists(1)
        GL.glNewList(self.objectDrawer, GL.GL_COMPILE)
        points = self.object.get_points()
        for face in self.object.get_faces():
            GL.glBegin(GL.GL_POLYGON)
            for i in face:
                point = points[i]
                GL.glVertex4fv(point)
            GL.glEnd()
        GL.glEndList()

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glMultMatrixf(self.frame.internal_camera_parameters.T)

        def rotate(self, rotation):
            for vector, angle in zip(((0, 0, 1), (0, 1, 0), (1, 0, 0)),
                                     reversed(rotation)):
                GL.glRotatef(angle, *vector)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslatef(*self.frame.camera_position.translation)
        self.rotate(self.frame.camera_position.orientation)
        GL.glTranslatef(*self.frame.object_position.translation)
        self.rotate(self.frame.object_position.orientation)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_TEXTURE_2D)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-1, 1, -1, 1, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)

        self.qglColor(Qt.white)
        self.drawTexture(QRectF(-1, -1, 2, 2), self.texture)

        GL.glDisable(GL.GL_TEXTURE_2D)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()

        GL.glMatrixMode(GL.GL_MODELVIEW)

        def drawObject(self):
            GL.glCallList(self.objectDrawer)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glColorMask(GL.GL_FALSE, GL.GL_FALSE, GL.GL_FALSE, GL.GL_FALSE)
        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
        self.qglColor(Qt.white)
        self.drawObject()
        GL.glPolygonMode(GL.GL_FRONT, GL.GL_LINE)
        GL.glColorMask(GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE)
        GL.glDepthMask(GL.GL_FALSE)
        self.qglColor(Qt.black)
        self.drawObject()
        GL.glDepthMask(GL.GL_TRUE)

        GL.glFlush()

    def resizeGL(self, w, h):
        x0, y0 = w // 2, h // 2
        image_w, image_h = self.frame.image.shape[1], self.frame.image.shape[0]
        coef = min(w / image_w, h / image_h)
        w, h = int(image_w * coef), int(image_h * coef)
        GL.glViewport(x0 - w // 2, y0 - h // 2, w, h)
