#!/usr/bin/env python
"""Installer for Cellular Automata Manager

Copyright 2013-2014 Mirco Tracolli.

This file is part of Cellular Automata Manager.
Cellular Automata Manager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cellular Automata Manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cellular Automata Manager.  If not, see <http://www.gnu.org/licenses/>.
"""
from setuptools import setup
import os, sys

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def main():
    r_pygame = False
    r_wxpython = False
    try:
        import pygame
        r_pygame = True
    except ImportError:
        print("This program requires pygame version >= 1.9.1")
    try:
        import wxPython
        r_wxpython = True
    except ImportError:
        print("This program requires wxPython version >= 2.8.12.0")
    
    if not r_pygame or not r_wxpython:
        sys.exit(1)
    
    setup(
        name='cellular-automata-manager',
        zip_safe=False,
        version="1.0",
        author="Tracolli Mirco",
        author_email='mirco.theone@gmail.com',
        description='Open source environment for cellular automata.',
        long_description='Open source environment for cellular automata written in Python.',
        url='https://github.com/MircoT/Cellular-Automata-Manager',
        license="GPLv3",
        keywords = "cellular automata environment simulation scintillae",
        setup_requires=["six>=1.4.1"],
        dependency_links = [
            "http://www.wxpython.org/download.php",
            "http://www.pygame.org/download.shtml"
        ],
        packages=['cae'],
        # To include data from MANIFEST.in for sdist
        include_package_data=True,
        package_dir={'cae': 'cae'},
        package_data={'cae':
            [
                "../assets/*.png",
                "../examples/*.cg",
                "../examples/old_examples/*.cg",
                "../doc/*.*",
                "../doc/img/*.png"
            ]
        },
        entry_points={
            'console_scripts': [
                'cam-env = cae.wxui:main'
            ]
        },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Topic :: Utilities",
            "Topic :: Education :: Testing",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        ],
        platforms=["windows", "mac", "linux"]
    )

if __name__ == '__main__':
    sys.exit(main())