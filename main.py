import os
import sys
from gui.main_window import MainWindow
from PySide import QtGui
from base.input_interface import loadWorkDir


def initialiseGui(obj, data):
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(data, obj)
    window.show()
    app.exec_()


def launch(workingDirectoryAddress):
    initialiseGui(*loadWorkDir(workingDirectoryAddress))


def demo():
    curPath = os.path.realpath(__file__)
    launch(os.path.join(os.path.dirname(curPath), "sample"))


arg = sys.argv[1]
if arg == '--demo':
    demo()
else:
    launch(arg)
