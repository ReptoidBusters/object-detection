# Object Detection

Edge-based and keypoint-based object detection algorithms

## Installation instructions

Using a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) 
is recommended. If you have Python 3.4+ and `pip` installed, you can install 
most of the project dependencies with

    pip install -r requirements.txt

Unfortunately installation of OpenCV for Python 3 is quite a bit trickier, but, 
luckily, there is a nice 
[guide](http://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/) 
for Ubuntu (same steps for any other Linux distribution). If you are using 
Windows, you can find 
[precompiled binaries](http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv) 
(requires wheel). You would also need 
[Visual C++ Redistributable for Visual Studio 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145) 
in this case.

TODO: Resolve problem with numpy.savetxt adding "#" between data
