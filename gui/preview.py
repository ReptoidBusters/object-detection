import cv2
from PySide.QtCore import QSize, QImage, QPixmap, Qt
from PySide.QtGui  import QWidget, QLabel


class KeyFramePreview(QWidget):
    """QtGui.QWidget for KeyFrame visualisation:
        image + matched object projection
    """

    def __init__(self, parent=None, _label, _keyframe, _object, *args, **kwargs):
        super().__init__(parent, *args, *kwargs)
        self.keyframe = _keyframe
        self.nameLabel = QLabel(_label)
        self.nameLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.object = _object
        self.isFull = False

    def mousePressEvent(self, event):
        self.resize(normalSize if self.isFull else self.parent().size())
        self.isFull ^= 1

    def resizeEvent(self, event):
        size = self.size()
        size.h -= 10
        self.imageLabel.resize(size)
        self.nameLabel.setGeometry(0, size.h, size.w, 10)
        image = cv2.resize(self.keyframe.image, size, 
                           interpolation=cv2.INTER_CUBIC)
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        pixmap = QPixmap(QImage(image.data, width, height, bytesPerLine, 
                         QImage.Format_RGB888))
        self.imageLabel.setPixmap(pixmap)
        raise NotImplemented("Object rendering")
