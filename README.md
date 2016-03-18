Cellular-Automata-Manager
=========================

## Description
Open source environment for cellular automata, useful to simulation and sperimentation.

## Dependencies

All dependencies are written in requirements.txt and you can install them with:
```bash
pip install -r requirements.txt
```

If you have some troubles, check how to install them on the main site of the libraries:
* wxPython - [dowload](http://www.wxpython.org/download.php#stable)
* PyOpenGL - [dowload](http://pyopengl.sourceforge.net)
* Pillow - [download](http://python-pillow.org)
* six - [dowload](https://pypi.python.org/pypi/six)

## Installation (optional)

To install the package, simply launch the command:
```bash
python setup.py install
```

## Make an executable

You can use [pyinstaller](http://www.pyinstaller.org/) to make a standalone executable of the program:
```bash
python main.spec main.py
```

## Run the application

If you have installed all the dependencies, you can run the program without install it with:
```bash
python main.py
```

If you have already installed the program with setuptools toolchain, you can run the application with:
```bash
cam-env
```

**Notes** : if you are under _Windows_, the _Script_ folder must be on your PATH variable. 
On _Linux_, if you can't start the application after a correct installation, try
to use the command ```which cam-env``` to search the executable. 

If you made an executable, you can run the application by running it.

For the moment is available also a temporary version of the executable for windows, useful if you want to use the program without install all the dependencies, also on linux and osx with [wine](https://www.winehq.org/). You can download it [here](https://dl.dropboxusercontent.com/u/16546001/cam.zip)

## Contributing

Contributions are welcome, so please feel free to fix bugs, improve things, provide documentation. 
For anything submit a personal message, thanks!



## License
The MIT License (MIT)

Copyright (c) 2016 Mirco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
