#########
SeeK-path
#########

Test status: branch `master`: |travismaster|; branch `develop`: |travisdevelop|

.. |travismaster| image:: https://travis-ci.org/giovannipizzi/seekpath.svg?branch=master
    :target: https://travis-ci.org/giovannipizzi/seekpath

.. |travisdevelop| image:: https://travis-ci.org/giovannipizzi/seekpath.svg?branch=develop
    :target: https://travis-ci.org/giovannipizzi/seekpath

``SeeK-path`` is a python module to obtain and visualize band paths in the
Brillouin zone of crystal structures. 

The definition of k-point labels follows crystallographic convention, as defined
and discussed in the `HPKOT paper`_. Moreover, the Bravais lattice is detected
properly using the spacegroup symmetry. Also the suggested band path provided
in the `HPKOT paper`_ is returned.
Systems without time-reversal and inversion-symmetry are also properly 
taken into account.

.. contents::

.. section-numbering::

===========
How to cite
===========
If you use this tool, please cite the following work:

- Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, *Band structure diagram 
  paths based on crystallography*, Comp. Mat. Sci. 128, 140 (2017)
  (`JOURNAL LINK`_, `arXiv link`_).
- You should also cite `spglib`_ that is an essential library used in the 
  implementation.

==============
How to install
==============
To install, use ``pip install seekpath``. It works both in python 2.7 and 
in python 3.5.

In some distributions (e.g. OpenSuse Leap 42.2), some additional libraries
might be needed, like `python3-devel` and `openblas-devel`.

If you want to start everything with Docker, follow the instructions on the `docker hub`_ page.

==========
How to use
==========
The main interface of the code is the python function 

    seekpath.get_path(structure, with_time_reversal, recipe, threshold)

You need to pass a crystal structure, a boolean flag (``with_time_reversal``) to say if time-reversal symmetry is present or not, and optionally, a recipe (currently only the string "HPKOT" is supported) and a numerical threshold.

The format of the structure is described in the function docstring. In particular,
It should be a tuple in the format 

``(cell, positions, numbers)``

where (if ``N`` is the number of atoms): 

- ``cell`` is a ``3x3`` list of floats (``cell[0]`` is the first lattice vector, ...); 
- ``positions`` is a ``Nx3`` list of floats with the atomic coordinates in scaled coordinates (i.e., w.r.t. the cell vectors);
- ``numbers`` is a length-``N`` list with integers identifying uniquely the atoms in the cell.

The output of the function is a dictionary containing, among other quantities, the k-vector coefficients, the suggested band path, whether the system has inversion symmetry, the crystallographic primitive lattice, the reciprocal primitive lattice.
A detailed description of all output information and their format can be found in the function docstring.

---------------------------------------------------------------
A warning on how to use (and crystal structure standardization)
---------------------------------------------------------------
SeeK-path standardizes the crystal structure 
(e.g., rotates the tetragonal system so that the *c* axis is along *z*, 
etc.) and can compute the suggested band paths only of standardized 
(crystallographic) primitive cells. Therefore, the 
**correct approach to use this tool is the following**:

1. You first find the standardized primitive cell with SeeK-path (returned in
   output) and store it somewhere, together with the k-point coordinates
   and suggested band path

2. You then run all your calculations using the standardized primitive cell

If you already have done calculations with a non-standardized cell, you will
then need to figure out how to remap the labeled k-points in the choice of
cell you did.

---------------
Explicit k path
---------------

You might also be interested in the function 

     seekpath.get_explicit_k_path

that has a very similar interface, that produces an explicit list of k-points along
the suggested band path. The function has the same interface as ``get_path``, but 
has also an additional optional parameter ``reference_distance``, that is used as a reference target distance between neighboring k-points along the path. More detailed information can be found in the docstrings.

=================
AiiDA integration
=================

If you use AiiDA (www.aiida.net), you might be interested in replacing the above
functions with the following wrappers, instead:

    seekpath.aiidawrappers.get_path 
    
    seekpath.aiidawrappers.get_explicit_k_path 

The function interfaces are very similar, but the advantage is that these functions expect an AiiDA structure as input (instead of a tuple) and return AiiDA structures and KpointsData classes instead of lists and tuples, where appropriate.
Also in this case, additional information is found in the docstrings.


=======
License
=======

The code is open-source (licensed with a MIT license, see LICENSE.txt).

===================
Online service/tool
===================

In this repository we also provide the code to deploy a online service for 
the visualization of the band paths and primitive cells of the crystal 
structures. A live demo is currently hosted on the `MaterialsCloud`_ web portal.

The following is a screenshot of the selection window:

.. image:: https://raw.githubusercontent.com/giovannipizzi/seekpath/master/webservice/screenshots/selector.png
     :alt: SeeK-path web service selection window
     :width: 50%
     :align: center

And the following is a screenshot of the main output window, showing the Brillouin zone, the primitive crystal structure, the coordinates of the k-points and the suggested band path.

.. image:: https://raw.githubusercontent.com/giovannipizzi/seekpath/master/webservice/screenshots/mainwindow.png
     :alt: SeeK-path web service main output
     :width: 50%
     :align: center

.. _HPKOT paper: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _JOURNAL LINK: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _arXiv link: https://arxiv.org/abs/1602.06402
.. _spglib: http://atztogo.github.io/spglib/
.. _MaterialsCloud: http://www.materialscloud.org/tools/seekpath/
.. _docker hub: https://hub.docker.com/r/giovannipizzi/seekpath/
