import collections
import argparse
import base
import sys
import os
from gui.preview import KeyFramePreview
from PySide import QtGui
from PySide.QtCore import Qt
from geometry import load_object


def read_args(args_list):
    return (input("Enter {}: ".format(arg)) for arg in args_list)


def initialiseGuiAndProcess(data, obj):
    app = QtGui.QApplication(sys.argv)

    window = QtGui.QMainWindow()
    window.setWindowTitle('Images')
    window.setFixedSize(1248, 702)
    window.setFocus()

    widget = QtGui.QWidget(window)
    layout = QtGui.QVBoxLayout(widget)
    for label, keyframe in data.items():
        layout.addWidget(KeyFramePreview(keyframe, obj, widget))
    widget.setLayout(layout)

    scroll = QtGui.QScrollArea()
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setWidgetResizable(False)
    scroll.setWidget(widget)

    window.setCentralWidget(widget)

    window.show()
    app.exec_()


def demo(number_of_inputs):
    name = "teapot"
    object_address = "samples/{}/mesh.obj".format(name)
    obj = load_object(object_address)
    data = {}
    counters = collections.defaultdict(int)
    method = base.input_interface.METHODS["two files"]
    for key, frame in method(name,
                             "samples/{}/image.png".format(name),
                             "samples/{0}/{0}".format(name)).load().items():
        counters[key] += 1
        if counters[key] > 1:
            key += str(counters[key])
        data[key] = frame
    print("Read finished", file=sys.stderr)
    initialiseGuiAndProcess(data, obj)


def cli(number_of_inputs):
    object_address = input("Input object file address: ")
    if not os.path.isfile(object_address):
        print(object_address, file=sys.stderr)
        raise LookupError("""No object file found at the given address or
                          reading is not permitted""")
    obj = load_object(object_address)
    data = {}
    counters = collections.defaultdict(int)
    for _ in range(number_of_inputs):
        method = base.input_interface.METHODS[input("Input method to use: ")]
        for key, frame in method(*read_args(method.input_list)).load().items():
            counters[key] += 1
            if counters[key] > 1:
                key += str(counters[key])
            data[key] = frame
    print("Read finished", file=sys.stderr)
    initialiseGuiAndProcess(data, obj)
    method = base.output_interface.METHODS[input("Output method to use: ")]
    method_args = read_args(method.input_list)
    if method == base.output_interface.BulkFolderWriter:
        method(data, *method_args).write()
    else:
        saved = 0
        for key, frame in data.items():
            method(frame, *read_args(method.input_list)).write()
            saved += 1
            if saved < len(data):
                method = base.output_interface.METHODS[input("""Output method to
                                                             use: """)]


parser = argparse.ArgumentParser(description='Process some keyframes.')
parser.add_argument('keyframes', metavar='N', type=int, nargs='?',
                    help='number of inputs', default=1)
parser.add_argument('--cli', dest='launch', action='store_const',
                    const=cli, default=cli,
                    help='''Launch the program in CLI mode (default will
                    be GUI once it is implemented)''')
parser.add_argument('--demo', dest='launch', action='store_const',
                    const=demo,
                    help='''Launch the program in demo mode''')

parser_args = parser.parse_args()
parser_args.launch(parser_args.keyframes)
