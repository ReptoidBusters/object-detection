try:
    from matching.chamfer import chamfer_matching
    from matching.blob import blob_matching
except ImportError:
    chamfer_matching = blob_matching = lambda: None

import sys
import os
from PySide import QtGui
from gui.preview import KeyFramePreview


class MainWindow(QtGui.QMainWindow):
    def __init__(self, data, obj):
        super().__init__()

        self.tabs = QtGui.QTabWidget(self)
        for label, keyframe in sorted(data.items()):
            self.tabs.addTab(KeyFramePreview(keyframe, obj, self.tabs), label)
        self.tabs.setMovable(True)
        self.setMinimumSize(960, 540)

        def call_matching(function, args):
            image_address = QtGui.QFileDialog.getOpenFileName(*args)
            if not image_address:
                print("Input cancelled", file=sys.stderr)
                return
            new_key_frame = function(data, image_address, obj)

            name_args = [args[0],
                         "New keyframe",
                         "How would like to call the new keyframe?"]

            name = QtGui.QInputDialog.getText(*name_args)
            self.tabs.addTab(KeyFramePreview(new_key_frame, obj, self.tabs),
                             name)

        args = [self.tabs,
                "Open Image",
                os.getcwd(),
                "Image Files (*.png *.jpg *.bmp)"]

        self.menu_bar = QtGui.QMenuBar(self)

        self.menu_bar.addAction("Blob matching",
                                lambda: call_matching(blob_matching, args))
        self.menu_bar.addAction("Chamfer matching",
                                lambda: call_matching(chamfer_matching, args))

    def resizeEvent(self, event):  # noqa
        width, height = event.size().width(), event.size().height()
        menu_bar_height = 20
        self.menu_bar.setGeometry(0, 0, width, menu_bar_height)
        self.tabs.setGeometry(0, menu_bar_height + 1, width,
                              height - menu_bar_height - 1)
