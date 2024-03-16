"""
The seekpath module contains routines to get automatically the
path in a 3D Brillouin zone to plot band structures.

Author: Giovanni Pizzi, PSI (2016-2023)

Licence: MIT License, see LICENSE.txt file
"""

__version__ = "2.1.0"
__author__ = "Giovanni Pizzi, PSI"
__copyright__ = (
    "Copyright (c), 2016-2023, Giovanni Pizzi, PAUL SCHERRER INSTITUT "
    "(Laboratory for Materials Simulations), EPFL "
    "(Theory and Simulation of Materials (THEOS) and National Centre "
    "for Computational Design and Discovery of Novel Materials "
    "(NCCR MARVEL)), Switzerland."
)
__credits__ = ["Yoyo Hinuma", "Jae-Mo Lihm"]
__license__ = "MIT license"
__paper__ = (
    "Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, "
    "Band structure diagram paths based on crystallography, "
    "Comp. Mat. Sci. 128, 140 (2017). DOI: 10.1016/j.commatsci.2016.10.015"
)


class SupercellWarning(UserWarning):
    """
    A warning issued when the cell is an undistorted supercell of a smaller
    unit cell, and the kpoint path for a non-standardized cell (i.e., for the
    original cell) is requested.
    """

    pass


from .getpaths import (
    get_path,
    get_explicit_k_path,
    get_path_orig_cell,
    get_explicit_k_path_orig_cell,
)

from .hpkot import EdgeCaseWarning, SymmetryDetectionError
from .brillouinzone import brillouinzone

__all__ = (
    "get_path",
    "get_explicit_k_path",
    "get_path_orig_cell",
    "get_explicit_k_path_orig_cell",
    "EdgeCaseWarning",
    "SymmetryDetectionError",
    "SupercellWarning",
    "brillouinzone"
)
