"""
The seekpath module contains routines to get automatically the
path in a 3D Brillouin zone to plot band structures.

Author: Giovanni Pizzi, EPFL (2016)

Licence: MIT License, see LICENSE.txt file
"""

__version__ = "1.0.2"
__author__ = "Giovanni Pizzi, EPFL"
__copyright__ = "Copyright (c), 2016, Giovanni Pizzi, EPFL (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland."
__credits__ = ["Yoyo Hinuma"]
__license__ = "MIT license"

from .getpaths import get_path, get_explicit_k_path
