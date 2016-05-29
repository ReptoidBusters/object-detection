import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from PySide.QtCore import QSize, QRectF
from PySide.QtGui import QImage
from PySide.QtOpenGL import QGLWidget


class KeyFramePreview(QGLWidget):
    """QtGui.QWidget for KeyFrame visualisation:
        image + matched object projection
    """

    normalSize = QSize(160, 90) * 2
    curSize = normalSize

    def __init__(self, _keyframe, _object, parent=None):
        QGLWidget.__init__(self, parent)
        self.frame = _keyframe
        self.object = _object

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glPolygonMode(GL_FRONT, GL_FILL)

        glColor3f(1.0, 1.0, 1.0)
        self.drawTexture(QRectF(-1, -1, 2, 2), self.texture)

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glDisable(GL_TEXTURE_2D)

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glColor3f(1.0, 1.0, 1.0)
        glPolygonMode(GL_FRONT, GL_FILL)
        self.drawObject()
        glColor3f(0.0, 0.0, 0.0)
        glPolygonMode(GL_FRONT, GL_LINE)
        self.drawObject()
        glFlush()

    def drawObject(self):
        for face in self.object.faces:
            glBegin(GL_POLYGON)
            for i in face:
                point = self.object.points[i]
                glVertex3f(point.x, point.y, point.z)
            glEnd()

    def rotate(self, rotation):
        for vector, angle in zip(((0, 0, 1), (0, 1, 0), (1, 0, 0)),
                                 reversed(rotation)):
            glRotatef(angle, *vector)

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1, 1)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)

        image = cv2.flip(self.frame.image, 0)
        height, width, channel = image.shape
        image = QImage(image.data, width, height, QImage.Format_RGB888)
        self.texture = self.bindTexture(image.rgbSwapped())

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(self.frame.internal_camera_parameters.T)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(*self.frame.camera_position.translation)
        self.rotate(self.frame.camera_position.orientation)
        glTranslatef(*self.frame.object_position.translation)
        self.rotate(self.frame.object_position.orientation)

    def mousePressEvent(self, event):
        self.curSize = (self.parent().size() if self.curSize == self.normalSize
                        else self.normalSize)
        self.resize(self.curSize)

    def resizeEvent(self, event):
        tmp = (self.curSize if self.curSize == self.normalSize
               else event.size())
        w, h = tmp.width(), tmp.height()
        print(w, h)
        self.setGeometry(10, 10, w, h)
        self.resizeGL(w, h)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
