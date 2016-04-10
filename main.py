import collections
import base
import cv2
import argparse


def read_args(args_list):
    return (input("Enter {}: ".format(arg)) for arg in args_list)


def cli(n):
    data = {}
    counters = collections.defaultdict(int)
    for i in range(n):
        method = base.input_interface.methods[input("Input method to use: ")]
        for key, frame in method(*read_args(method.input_list)).load().items():
            counters[key] += 1
            if counters[key] > 1:
                key += str(counters[key])
            data[key] = frame
    print("Read finished")
    # here should be some processing
    pass
    #
    method = base.output_interface.methods[input("Output method to use: ")]
    args = read_args(method.input_list)
    if method == base.output_interface.BulkFolderWriter:
        method(data, *args).write()
    else:
        saved = 0
        for key, frame in data.items():
            method(frame, *read_args(method.input_list)).write()
            saved += 1
            if saved < len(data):
                method = base.output_interface.methods[input("""Output method to 
                                                             use: """)]


parser = argparse.ArgumentParser(description = 'Process some keyframes.')
parser.add_argument('keyframes', metavar = 'N', type = int, nargs = '?',
                   help = 'number of inputs', default = 1)
parser.add_argument('--cli', dest = 'launch', action = 'store_const',
                   const = cli, default = cli,
                   help = '''Launch the program in CLI mode (default will be GUI
                   once it is implemented)''')

args = parser.parse_args()
args.launch(args.keyframes)