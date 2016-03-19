import numpy
import cv2
import base

n = int(input("Number of inputs: "))
data = []
for i in range(n):
    method = base.input_interface.methods[input("Input method to use: ")]
    data.append(method(*method.readArguments()).read())
print("Read finished")

print("Now I'll emulate I'm doing something")
N = 1000000
for x in range(0, N + 1):
    print(int(x / N * 100), end = "%\r")
print("Done!")

for i in range(n):
    method = base.output_interface.methods[input("Output method to use: ")]
    method(*method.readArguments()).save()
