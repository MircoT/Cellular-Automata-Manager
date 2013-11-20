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
* pygame - [dowload](http://www.pygame.org/download.shtml)
* six - [dowload](https://pypi.python.org/pypi/six)

## Installation

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

## Contributing

Contributions are welcome, so please feel free to fix bugs, improve things, provide documentation. 
For anything submit a personal message, thanks!



## License
Copyright (C) 2013  Mirco Tracolli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
