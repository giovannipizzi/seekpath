#########
SeeK-path
#########

Test status for default branch: |continuousintegration|

.. |continuousintegration| image:: https://github.com/giovannipizzi/seekpath/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/giovannipizzi/seekpath/actions/workflows/ci.yml

``SeeK-path`` is a python module to obtain band paths in the
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
  implementation: A. Togo, I. Tanaka,
  "Spglib: a software library for crystal symmetry search", arXiv:1808.01590 (2018) (`spglib arXiv link`_).

=============================
How to install and how to use
=============================

Please check the SeeK-path `user guide on ReadTheDocs`_.

================
Acknowledgements
================

* Jae-Mo Lihm: k-point paths for the original unit cell (i.e., the one provided in input by the user) without standardization or symmetrization

=======
License
=======

The code is open-source (licensed with a MIT license, see LICENSE.txt).

===================
Online service/tool
===================

In the `tools-seekpath`_ repository we also provide the code to deploy a online service for
the visualization of the band paths and primitive cells of the crystal
structures. A live version is hosted on the `Materials Cloud`_ web portal.

The following is a screenshot of the selection window:

.. image:: https://raw.githubusercontent.com/materialscloud-org/tools-seekpath/master/misc/screenshots/selector.png
     :alt: SeeK-path web service selection window
     :width: 50%
     :align: center

And the following is a screenshot of the main output window, showing the Brillouin zone, the primitive crystal structure, the coordinates of the k-points and the suggested band path.

.. image:: https://raw.githubusercontent.com/materialscloud-org/tools-seekpath/master/misc/screenshots/mainwindow.png
     :alt: SeeK-path web service main output
     :width: 50%
     :align: center

.. _HPKOT paper: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _JOURNAL LINK: http://dx.doi.org/10.1016/j.commatsci.2016.10.015
.. _arXiv link: https://arxiv.org/abs/1602.06402
.. _spglib: http://atztogo.github.io/spglib/
.. _Materials Cloud: http://www.materialscloud.org/tools/seekpath/
.. _docker hub: https://hub.docker.com/r/giovannipizzi/seekpath/
.. _user guide on ReadTheDocs: http://seekpath.readthedocs.io
.. _spglib arXiv link: https://arxiv.org/abs/1808.01590
.. _tools-seekpath: http://www.github.com/materialscloud-org/tools-seekpath/
