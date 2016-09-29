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
