SeeK-path
=========

``SeeK-path`` is a module to obtain and visualize band paths in the Brillouin
zone of crystal structures. 

The definition of k-point labels follows crystallographic convention, as defined
and discussed in the `HPKOT paper`_. Moreover, the Bravais lattice is detected
properly using the spacegroup symmetry. Also the suggested band path provided
in the `HPKOT paper`_ is returned.
Systems without time-reversal and inversion-symmetry are also properly 
taken into account.

How to cite
-----------
If you use this tool, please cite the following work:

- Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, *Band structure diagram 
  paths based on crystallography*, arXiv:1602.06402 (2016) (`JOURNAL LINK`_).
- You should also cite `spglib`_ that is an essential library used in the 
  implementation.

How to install
--------------
To install, use ``pip install seekpath``.

How to use
----------
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

You might also be interested in the function 

     seekpath.get_explicit_k_path

that has a very similar interface, that produces an explicit list of k-points along
the suggested band path. The function has the same interface as ``get_path``, but 
has also an additional optional parameter ``reference_distance``, that is used as a reference target distance between neighboring k-points along the path. More detailed information can be found in the docstrings.

AiiDA integration
+++++++++++++++++
If you use AiiDA (www.aiida.net), you might be interested in replacing the above
functions with the following wrappers, instead:

    seekpath.aiidawrappers.get_path 
    
    seekpath.aiidawrappers.get_explicit_k_path 

The function interfaces are very similar, but the advantage is that these functions expect an AiiDA structure as input (instead of a tuple) and return AiiDA structures and KpointsData classes instead of lists and tuples, where appropriate.
Also in this case, additional information is found in the docstrings.


License
-------
The code is open-source (licensed with a MIT license, see LICENSE.txt).

Online service/tool
-------------------
In this repository we also provide the code to deploy a online service for 
the visualization of the band paths and primitive cells of the crystal 
structures. A live demo is currently hosted on the `MaterialsCloud`_ web portal.

The following is a screenshot of the selection window:

.. image:: https://raw.githubusercontent.com/giovannipizzi/seekpath/master/webservice/screenshots/selector.png
     :alt: SeeK-path web service selection window
     :width: 80%
     :align: center

And the following is a screenshot of the main output window, showing the Brillouin zone, the primitive crystal structure, the coordinates of the k-points and the suggested band path.

.. image:: https://raw.githubusercontent.com/giovannipizzi/seekpath/master/webservice/screenshots/mainwindow.png
     :alt: SeeK-path web service main output
     :width: 80%
     :align: center

.. _HPKOT paper: http://arxiv.org/abs/1602.06402
.. _JOURNAL LINK: http://arxiv.org/abs/1602.06402
.. _spglib: http://atztogo.github.io/spglib/
.. _MaterialsCloud: http://www.materialscloud.org/tools/seekpath/
