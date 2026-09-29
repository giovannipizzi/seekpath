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

    seekpath.get_path(structure, with_time_reversal, recipe, threshold, symprec, angle_tolerance, backend)

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
e.g. the order of axes in an orthorhombic cell; instead ``symprec`` and ``angle_tolerance`` are just passed to the symmetry backend).

------------------
Symmetry backends
------------------

The symmetry analysis that standardizes the input structure is done by
`spglib`_ by default. Passing ``backend='moyopy'`` uses `moyopy`_ instead, a
Rust reimplementation of spglib::

    seekpath.get_path(structure, backend='moyopy')

``moyopy`` is an optional dependency that requires Python >= 3.10, installed
with::

    pip install seekpath[moyopy]

What agrees
~~~~~~~~~~~

:py:func:`~seekpath.getpaths.get_path` and
:py:func:`~seekpath.getpaths.get_explicit_k_path` give the **same** result with
either backend. For all 60 reference structures shipped with seekpath, with and
without time reversal, the Bravais lattice classification, the extended Bravais
symbol, the space group, the path, the k-point labels and their coordinates are
identical, and the primitive lattices agree to within 1e-10. This also holds
under random rotations and unimodular changes of the input basis, for
left-handed input bases, and for supercells. Only the atom positions in the
standardized cells can differ (case 4).

What can differ
~~~~~~~~~~~~~~~

Four cases are known. None of them makes one backend right and the other wrong,
but they are worth knowing about before switching an existing workflow.

**1. K-points in the basis of the original cell.**
:py:func:`~seekpath.getpaths.get_path_orig_cell` and
:py:func:`~seekpath.getpaths.get_explicit_k_path_orig_cell` express the k-points
in the basis of the *input* cell. That depends on which of the several
symmetry-equivalent alignments of the standardized cell the backend picked, and
the two libraries do not always pick the same one.

For 25 of the 60 reference structures the two backends give identical
k-points. For the other 35 the k-points differ by an integral operation in the
conventional basis, most often a 180 or 120 degree rotation, and the two paths
are symmetry-equivalent (allowing for time reversal) in every case: a band
structure computed along either is the same, but the numbers are not
identical. Code that compares ``get_path_orig_cell`` output against stored
k-points should therefore not switch backend without re-generating them.

**2. Very loose** ``symprec`` **, right at a symmetry-promotion threshold.**
Where a structure sits on the boundary between two space groups, the two
libraries cross that boundary at slightly different tolerances, because they
apply ``symprec`` to different measures of the atomic mismatch: ``moyopy``
promotes to the higher-symmetry group at the smaller tolerance of the two.
Displacing every atom of each reference structure by 0.02 Angstrom and raising
``symprec`` until the undistorted space group is recovered, ``spglib`` needs a
tolerance 1.1 to 2.0 times larger than ``moyopy`` does (median 1.7 over the 28
structures where both recover it). Away from such a boundary the two agree over
the whole practical range.
If a structure's space group changes when ``symprec`` is nudged, that is a sign
the tolerance is too loose to be meaningful, whichever backend is used.

**3. Triclinic cells with 90 degree reciprocal angles (** ``aP2`` **vs** ``aP3``
**).** A triclinic crystal sitting on a higher-symmetry lattice - a defect cell
or a substituted supercell, say - can be classified either way, because the test
that separates the two looks at the sign of a quantity that is exactly zero.
This is **not** a backend difference: the spglib backend alone returns both
answers for the same crystal supplied in different orientations. seekpath raises
:py:class:`~seekpath.hpkot.EdgeCaseWarning` when it happens, and that warning
should be taken seriously whichever backend is in use.

**4. Atom positions in the standardized cell.** The two libraries may choose
different, symmetry-equivalent origins, so ``conv_positions`` and
``primitive_positions`` can differ by a shift (and in atom order). This does not
affect the k-paths, which are origin-independent.

.. note:: For a supercell whose lattice has lower symmetry than the crystal
    itself, ``moyopy`` logs a warning that it omitted some symmetry operations.
    seekpath does not use these operations, so the warning does not affect its
    results. It can be silenced with
    ``logging.getLogger('moyo').setLevel(logging.ERROR)``.

Performance
~~~~~~~~~~~

``moyopy`` is the faster of the two across the board. Measured through
:py:func:`~seekpath.getpaths.get_path` on rocksalt supercells, either perfect or
with every atom displaced slightly to break the supercell symmetry:

=============================  ==========  ==========
cell                           ``spglib``  ``moyopy``
=============================  ==========  ==========
128 atoms, low symmetry        2.7 ms      1.6 ms
432 atoms, low symmetry        17.8 ms     8.4 ms
1024 atoms, low symmetry       87.3 ms     34.4 ms
128 atoms, perfect supercell   9.0 ms      1.0 ms
432 atoms, perfect supercell   10.0 ms     2.8 ms
1024 atoms, perfect supercell  14.7 ms     11.3 ms
=============================  ==========  ==========

The speedup grows with the number of atoms for a low-symmetry cell, and shrinks
for a large perfect supercell, where ``spglib`` scales well because it reduces
to the primitive cell early.


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
https://aiida-core.readthedocs.io/en/latest/datatypes/kpoints.html


.. _HPKOT paper: https://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _JOURNAL LINK: https://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _arXiv link: https://arxiv.org/abs/1602.06402
.. _spglib: https://atztogo.github.io/spglib/

.. _moyopy: https://spglib.github.io/moyo/python/
.. _Materials Cloud: https://www.materialscloud.org/tools/seekpath/
.. _docker hub: https://hub.docker.com/r/giovannipizzi/seekpath/
.. _AiiDA: https://www.aiida.net
.. _spglib arXiv link: https://arxiv.org/abs/1808.01590
