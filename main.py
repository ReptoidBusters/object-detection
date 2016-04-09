import base

n = int(input("Number of inputs: "))
data = []
for i in range(n):
    method = base.input_interface.methods[input("Input method to use: ")]
    data.append(method(*method.readArguments()).read())
print("Read finished")

for frame in data:
    method = base.output_interface.methods[input("Output method to use: ")]
    method(frame).save(*method.readArguments())
