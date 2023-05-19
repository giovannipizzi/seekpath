Welcome to documentation of SeeK-path
=====================================

``SeeK-path`` is a python module to obtain and visualize band paths in the
Brillouin zone of crystal structures.

The definition of k-point labels follows crystallographic convention, as defined
and discussed in the `HPKOT paper`_. Moreover, the Bravais lattice is detected
properly using the spacegroup symmetry. Also the suggested band path provided
in the `HPKOT paper`_ is returned.
Systems without time-reversal and inversion-symmetry are also properly
taken into account.


===========
How to cite
===========
If you use this tool, please cite the following work:

- Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, *Band structure diagram
  paths based on crystallography*, Comp. Mat. Sci. 128, 140 (2017)
  (`JOURNAL LINK`_, `arXiv link`_).
- You should also cite `spglib`_ that is an essential library used in the
  implementation: A. Togo, I. Tanaka,
  "Spglib: a software library for crystal symmetry search", arXiv:1808.01590 (2018) (`spglib arXiv link`_).


==============
How to install
==============
To install, use ``pip install seekpath``. It works both in python 2.7 and
in python 3.5.

In some distributions (e.g. OpenSuse Leap 42.2), some additional libraries
might be needed, like `python3-devel` and `openblas-devel`.

If you want to start everything with Docker, you can use the ``Dockerfile`` provided,
or directly the images on `docker hub`_.

==========
How to use
==========
The main interface of the code is the :py:func:`~seekpath.getpaths.get_path` python function::

    seekpath.get_path(structure, with_time_reversal, recipe, threshold, symprec, angle_tolerance)

You need to pass a crystal structure, a boolean flag (``with_time_reversal``) to say if time-reversal symmetry is present or not, and optionally, a recipe (currently only the string ``hpkot`` is supported) and a numerical threshold.

The format of the structure is described in the function docstring. In particular,
It should be a tuple in the format::

  (cell, positions, numbers)

where (if ``N`` is the number of atoms):

- ``cell`` is a ``3x3`` list of floats (``cell[0]`` is the first lattice vector, ...);
- ``positions`` is a ``Nx3`` list of floats with the atomic coordinates in scaled coordinates (i.e., w.r.t. the cell vectors);
- ``numbers`` is a length-``N`` list with integers identifying uniquely the atoms in the cell.

The output of the function is a dictionary containing, among other quantities, the k-vector coefficients, the suggested band path, whether the system has inversion symmetry, the crystallographic primitive lattice, the reciprocal primitive lattice.
A detailed description of all output information and their format can be found in the function docstring. (Note that the ``threshold`` is the one used by seekpath to identify
e.g. the order of axes in an orthorhombic cell; instead ``symprec`` and ``angle_tolerance`` are just passed to spglib).

----------------------------------------
K-point path for non-standard unit cells
----------------------------------------

If you want a k-point path for a non-standardized cell, for example because you
already have done calculations with a non-standardized cell, you can use the
:py:func:`~seekpath.getpaths.get_path_orig_cell` function::

     seekpath.get_path_orig_cell

If the input cell is a non-standard primitive unit cell, the returned k path is equivalent to the k path for the standard cell.
For example, the band structure calculated along the k path for the standard and non-standard unit cells will be the same up to numerical errors.

If the input cell is a supercell of a smaller primitive cell, the returned k path is that of the associated primitive cell, in the basis of supercell reciprocal lattice.
In this case, the k points are **not** the high-symmetry points of the first Brillouin zone of the given supercell, but the high-symmetry points of the Brillouin zone of the associated primitive cell.

**Note that contrary to ``get_path``, ``get_path_orig_cell`` calculates the k path based on the symmetrized structure but does not symmetrize the input structure itself.**
Hence, if the symmetry of the input structure is slightly broken below the symmetry precision ``symprec``, the **output k points may not be exactly on the high-symmetry k points.**

---------------------------------------------------------------
A warning on how to use (and crystal structure standardization)
---------------------------------------------------------------
The ``get_path`` and ``get_explicit_k_path`` functions standardizes the crystal structure
(e.g., rotates the tetragonal system so that the *c* axis is along *z*,
etc.) and can compute the suggested band paths only of standardized
(crystallographic) primitive cells. The
**correct approach to use these functions is the following**:

1. You first find the standardized primitive cell with SeeK-path (returned in
   output) and store it somewhere, together with the k-point coordinates
   and suggested band path

2. You then run all your calculations using the standardized primitive cell

If you want a k-point path for a non-standardized cell, you can use the
``get_path_orig_cell`` and ``get_explicit_k_path_orig_cell`` functions: see the above subsection (and in particular, check the limitations if the symmetry of the input structure is slightly broken).

---------------
Explicit k path
---------------

You might also be interested in the :py:func:`~seekpath.getpaths.get_explicit_k_path` function::

     seekpath.get_explicit_k_path

that has a very similar interface, that produces an explicit list of k-points along
the suggested band path. The function has the same interface as :py:func:`~seekpath.getpaths.get_path`, but
has also an additional optional parameter ``reference_distance``, that is used as a reference target distance between neighboring k-points along the path. More detailed information can be found in the docstrings of :py:func:`~seekpath.getpaths.get_explicit_k_path`.

An analogous function that gives the explicit list of k-points for the original (possibly non-standard) cell also exists. :py:func:`~seekpath.getpaths.get_explicit_k_path_orig_cell`::

     seekpath.get_explicit_k_path_orig_cell

=================
AiiDA integration
=================
If you use AiiDA, you might be interested to use the wrappers that are provided in AiiDA.

The documentation of the methods can be found at
http://aiida-core.readthedocs.io/en/latest/datatypes/kpoints.html


.. _HPKOT paper: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _JOURNAL LINK: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _arXiv link: https://arxiv.org/abs/1602.06402
.. _spglib: http://atztogo.github.io/spglib/
.. _Materials Cloud: http://www.materialscloud.org/tools/seekpath/
.. _docker hub: https://hub.docker.com/r/giovannipizzi/seekpath/
.. _AiiDA: http://www.aiida.net
.. _spglib arXiv link: https://arxiv.org/abs/1808.01590
