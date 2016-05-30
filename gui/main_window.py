import sys
import os
from PySide import QtGui
from gui.preview import KeyFramePreview


def raiseNotImplemented():
    raise NotImplemented

try:
    from matching.chamfer import chamfer_matching
    from matching.blob import blob_matching
except:
    chamfer_matching = blob_matching = raiseNotImplemented


class MainWindow(QtGui.QMainWindow):
    def __init__(self, data, obj):
        super().__init__()

        self.tabs = QtGui.QTabWidget(self)
        for label, keyframe in sorted(data.items()):
            self.tabs.addTab(KeyFramePreview(keyframe, obj, self.tabs), label)
        self.tabs.setMovable(True)
        self.setMinimumSize(960, 540)

        def callMatching(function, args):
            imageAddress = QtGui.QFileDialog.getOpenFileName(*args)
            if not imageAddress:
                print("Input cancelled", file=sys.stderr)
                return
            newKeyFrame = function(data, imageAddress, obj)

            nameArgs = [args[0],
                        "New keyframe",
                        "How would like to call the new keyframe?"]

            name = QtGui.QInputDialog.getText(*nameArgs)
            self.tabs.addTab(KeyFramePreview(newKeyFrame, obj, self.tabs),
                             name)

        args = [self.tabs,
                "Open Image",
                os.getcwd(),
                "Image Files (*.png *.jpg *.bmp)"]

        self.menuBar = QtGui.QMenuBar(self)

        self.menuBar.addAction("Blob matching",
                               lambda: callMatching(blob_matching, args))
        self.menuBar.addAction("Chamfer matching",
                               lambda: callMatching(chamfer_matching, args))

    def resizeEvent(self, event):
        w, h = event.size().width(), event.size().height()
        H = 20
        self.menuBar.setGeometry(0, 0, w, H)
        self.tabs.setGeometry(0, H + 1, w, h - H - 1)
