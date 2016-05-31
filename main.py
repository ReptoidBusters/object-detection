import os
import sys
from PySide import QtGui
from gui.main_window import MainWindow
from base.input_interface import load_work_dir


def initialise_gui(obj, data):
    window = MainWindow(data, obj)
    window.show()
    app.exec_()


def launch(working_directory_address):
    initialise_gui(*load_work_dir(working_directory_address))


def demo():
    cur_path = os.path.realpath(__file__)
    launch(os.path.join(os.path.dirname(cur_path), "sample"))


if sys.argv[1] != '--demo':
    launch(sys.argv[1])
else:
    demo()
