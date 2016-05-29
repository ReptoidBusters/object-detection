import cv2
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
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
        w, h = self.frame.image.shape[1], self.frame.image.shape[0]
        self.setGeometry(0, 0, w, h)
        glViewport(0, 0, w, h)

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

        self.qglColor(Qt.white)
        self.drawTexture(QRectF(-1, -1, 2, 2), self.texture)

        glDisable(GL_TEXTURE_2D)

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glPolygonMode(GL_FRONT, GL_FILL)
        self.qglColor(Qt.white)
        self.drawObject()
        glPolygonMode(GL_FRONT, GL_LINE)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glDepthMask(GL_FALSE)
        self.qglColor(Qt.black)
        self.drawObject()
        glDepthMask(GL_TRUE)

        glFlush()

    def drawObject(self):
        glCallList(self.objectDrawer)

    def rotate(self, rotation):
        for vector, angle in zip(((0, 0, 1), (0, 1, 0), (1, 0, 0)),
                                 reversed(rotation)):
            glRotatef(angle, *vector)

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1, 1)

        image = cv2.flip(self.frame.image, 0)
        height, width, channel = image.shape
        image = QImage(image.data, width, height, QImage.Format_RGB888)
        self.texture = self.bindTexture(image.rgbSwapped())

        self.objectDrawer = glGenLists(1)
        glNewList(self.objectDrawer, GL_COMPILE)
        points = self.object.get_points()
        print(np.array(points))
        print(np.array(self.object.get_faces()))
        for face in self.object.get_faces():
            glBegin(GL_POLYGON)
            for i in face:
                point = points[i]
                glVertex4fv(point)
            glEnd()
        glEndList()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(self.frame.internal_camera_parameters.T)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(*self.frame.camera_position.translation)
        self.rotate(self.frame.camera_position.orientation)
        glTranslatef(*self.frame.object_position.translation)
        self.rotate(self.frame.object_position.orientation)
