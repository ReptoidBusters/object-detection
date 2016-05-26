import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from PySide.QtCore import QSize, QImage, QPixmap
from PySide.QtGui import QGLWidget


class KeyFramePreview(QGLWidget):
    """QtGui.QWidget for KeyFrame visualisation:
        image + matched object projection
    """

    normalSize = QSize(160, 90)

    def __init__(self, _keyframe, _object, parent=None):
        QGLWidget.__init__(self, parent)
        self.frame = _keyframe
        self.object = _object
        self.setMinimumSize(normalSize)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glColor3f(1.0, 1.0, 1.0)
        glPolygonMode(GL_FRONT, GL_FILL)
        self.drawObject()
        glColor3f(0.0, 0.0, 0.0)
        glPolygonMode(GL_FRONT, GL_LINE)
        self.drawObject(reversed=True)
        glFlush()

    def drawObject(reversed=False):
        for face in self.object.faces:
            glBegin(GL_POLYGON)
            for i in (reversed(face) if reversed else face):
                point = self.object.points[i]
                glVertex3f(point.x, point.y, point.z)
        glEnd()

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glTranslatef(*_keyframe.object_position.translation)
        glRotatef(*_keyframe.object_position.rotation)
        glLoadIdentity()
        gluPerspective(45.0, 1.33, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(*_keyframe.camera_position.translation)
        glRotatef(*_keyframe.camera_position.rotation)

    def mousePressEvent(self, event):
        self.resize(self.normalSize if self.isFull else self.parent().size())
        self.isFull ^= 1

    def resizeGL(w, h):
        image = cv2.resize(self.keyframe.image, (w, h),
                           interpolation=cv2.INTER_CUBIC)
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        pixmap = QPixmap(QImage(image.data, width, height, bytesPerLine,
                                QImage.Format_RGB888))
        self.imageLabel.setPixmap(pixmap)
        self.nameLabel.setGeometry(0, size.h, size.w, 10)
