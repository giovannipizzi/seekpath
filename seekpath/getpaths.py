"""
This module contains the main functions to get a path and an explicit path.
"""
import numpy as np
import warnings
from . import SupercellWarning


def get_explicit_from_implicit(  # pylint: disable=too-many-locals
    seekpath_output, reference_distance
):
    """
    Given the output of ``get_path`` by seekpath, compute an "explicit" path,
    i.e. instead of just giving the endpoints and their coordinates, compute
    a full list of kpoints

    :param seekpath_output: a dictionary, the output of ``seekpath.get_path``

    :param reference_distance: a reference target distance between neighboring
        k-points in the path, in units of 1/ang. The actual value will be as
        close as possible to this value, to have an integer number of points in
        each path.
    """
    retdict = {}

    kpoints_rel = []
    kpoints_labels = []
    kpoints_linearcoord = []
    previous_linearcoord = 0.0
    segments = []
    for start_label, stop_label in seekpath_output["path"]:
        start_coord = np.array(seekpath_output["point_coords"][start_label])
        stop_coord = np.array(seekpath_output["point_coords"][stop_label])
        start_coord_abs = np.dot(
            start_coord, seekpath_output["reciprocal_primitive_lattice"]
        )
        stop_coord_abs = np.dot(
            stop_coord, seekpath_output["reciprocal_primitive_lattice"]
        )
        segment_length = np.linalg.norm(stop_coord_abs - start_coord_abs)
        num_points = max(2, int(segment_length / reference_distance))
        segment_linearcoord = np.linspace(0.0, segment_length, num_points)
        segment_start = len(kpoints_labels)
        for i in range(num_points):
            # Skip the first point if it's the same as the last one of
            # the previous segment
            if i == 0:
                if kpoints_labels:
                    if kpoints_labels[-1] == start_label:
                        segment_start -= 1
                        continue

            kpoints_rel.append(
                start_coord
                + (stop_coord - start_coord) * float(i) / float(num_points - 1)
            )
            if i == 0:
                kpoints_labels.append(start_label)
            elif i == num_points - 1:
                kpoints_labels.append(stop_label)
            else:
                kpoints_labels.append("")
            kpoints_linearcoord.append(previous_linearcoord + segment_linearcoord[i])
        previous_linearcoord += segment_length
        segment_end = len(kpoints_labels)
        segments.append((segment_start, segment_end))

    retdict["kpoints_rel"] = np.array(kpoints_rel)
    retdict["kpoints_linearcoord"] = np.array(kpoints_linearcoord)
    retdict["kpoints_labels"] = kpoints_labels
    retdict["kpoints_abs"] = np.dot(
        retdict["kpoints_rel"], seekpath_output["reciprocal_primitive_lattice"]
    )
    retdict["segments"] = segments

    return retdict


def get_path(
    structure,
    with_time_reversal=True,
    recipe="hpkot",
    threshold=1.0e-7,
    symprec=1e-05,
    angle_tolerance=-1.0,
):
    r"""
    Return the kpoint path information for band structure given a
    crystal structure, using the paths from the chosen recipe/reference.

    If you use this module, please cite the paper of the corresponding
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: ``(cell, positions, numbers)``, where
        (if N is the number of atoms):

        - ``cell`` is a :math:`3 \times 3` list of floats (``cell[0]`` is the first lattice
          vector, ...)
        - ``positions`` is a :math:`N \times 3` list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - ``numbers`` is a length-:math:`N` list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

    :param with_time_reversal: if False, and the group has no inversion
        symmetry, additional lines are returned as described in the HPKOT
        paper.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:

       - ``hpkot``: HPKOT paper:
         Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure
         diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
         DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in
        and edge case (e.g., a tetragonal cell, but ``a==c``). For instance,
        in the tI lattice, if ``abs(a-c) < threshold``, a
        :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued.
        Note that depending on the bravais lattice, the meaning of the
        threshold is different (angle, length, ...)

    :param symprec: the symmetry precision used internally by SPGLIB

    :param angle_tolerance: the angle_tolerance used internally by SPGLIB


    :return: a dictionary with the following
      keys:

        - ``point_coords``: a dictionary with label -> float coordinates
        - ``path``: a list of length-2 tuples, with the labels of the starting
          and ending point of each label section
        - ``has_inversion_symmetry``: True or False, depending on whether the
          input crystal structure has inversion symmetry or not.
        - ``augmented_path``: if True, it means that the path was
          augmented with the :math:`-k` points (this happens if both
          has_inversion_symmetry is False, and the user set
          with_time_reversal=False in the input)
        - ``bravais_lattice``: the Bravais lattice string (like ``cP``, ``tI``, ...)
        - ``bravais_lattice_extended``: the specific case used to define labels and
          coordinates (like ``cP1``, ``tI2``, ...)
        - ``cont_lattice``: three real-space vectors for the crystallographic
          conventional cell (``conv_lattice[0,:]`` is the first vector)
        - ``conv_positions``: fractional coordinates of atoms in the
          crystallographic conventional cell
        - ``conv_types``: list of integer types of the atoms in the crystallographic
          conventional cell (typically, the atomic numbers)
        - ``primitive_lattice``: three real-space vectors for the crystallographic
          primitive cell (``primitive_lattice[0,:]`` is the first vector)
        - ``primitive_positions``: fractional coordinates of atoms in the
          crystallographic primitive cell
        - ``primitive_types``: list of integer types of the atoms in the
          crystallographic primitive cell (typically, the atomic numbers)
        - ``reciprocal_primitive_lattice``: reciprocal-cell vectors for the
          primitive cell (vectors are rows: ``reciprocal_primitive_lattice[0,:]``
          is the first vector)
        - ``primitive_transformation_matrix``: the transformation matrix :math:`P` between
          the conventional and the primitive cell
        - ``inverse_primitive_transformation_matrix``: the inverse of the matrix :math:`P`
          (the determinant is integer and gives the ratio in volume between
          the conventional and primitive cells)
        - ``volume_original_wrt_conv``: volume ratio of the user-provided cell
          with respect to the the crystallographic conventional cell
        - ``volume_original_wrt_prim``: volume ratio of the user-provided cell
          with respect to the the crystalloraphic primitive cell

    :note: An :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued for
        edge cases (e.g. if ``a==b==c`` for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    if recipe == "hpkot":
        from . import hpkot

        res = hpkot.get_path(
            structure=structure,
            with_time_reversal=with_time_reversal,
            threshold=threshold,
            symprec=symprec,
            angle_tolerance=angle_tolerance,
        )

    else:
        raise ValueError(
            "value for 'recipe' not recognized. The only value "
            "currently accepted is 'hpkot'."
        )
    return res


def get_explicit_k_path(
    structure,
    with_time_reversal=True,
    reference_distance=0.025,
    recipe="hpkot",
    threshold=1.0e-7,
    symprec=1e-05,
    angle_tolerance=-1.0,
):
    r"""
    Return the kpoint path for band structure (in scaled and absolute
    coordinates), given a crystal structure,
    using the paths proposed in the various publications (see description
    of the 'recipe' input parameter).
    Note that the k-path typically refers to a different unit cell
    (e.g., the primitive one with some transformation matrix to comply with
    the conventions in the case of the HPKOT paper). So, one should use the
    crystal cell provided in output for all calculations, rather than the
    input 'structure'.

    If you use this module, please cite the paper of the corresponding
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: (cell, positions, numbers), where
        (if N is the number of atoms):

        - ``cell`` is a :math:`3 \times 3` list of floats (``cell[0]`` is the first lattice
          vector, ...)
        - ``positions`` is a :math:`N \times 3` list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - ``numbers`` is a length-:math:`N` list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

    :param with_time_reversal: if False, and the group has no inversion
        symmetry, additional lines are returned.

    :param reference_distance: a reference target distance between neighboring
        k-points in the path, in units of 1/ang. The actual value will be as
        close as possible to this value, to have an integer number of points in
        each path.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:

       - ``hpkot``: HPKOT paper:
         Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure
         diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
         DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in
        and edge case (e.g., a tetragonal cell, but ``a==c``). For instance,
        in the tI lattice, if ``abs(a-c) < threshold``, a
        :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued.
        Note that depending on the bravais lattice, the meaning of the
        threshold is different (angle, length, ...)

    :param symprec: the symmetry precision used internally by SPGLIB

    :param angle_tolerance: the angle_tolerance used internally by SPGLIB

    .. versionchanged:: 1.8
        The key ``segments`` has been renamed ``explicit_segments``
        for consistency.

    :return: a dictionary with a number of keys. They are the same as
        ``get_path``, plus a few ones:

        - ``explicit_kpoints_abs``: List of the kpoints along the specific path in
          absolute (Cartesian) coordinates. The two endpoints are always
          included, independently of the length.
        - ``explicit_kpoints_rel``: List of the kpoints along the specific path in
          relative (fractional) coordinates (same length as
          explicit_kpoints_abs).
        - ``explicit_kpoints_labels``: list of strings with kpoints labels. It has
          the same length as explicit_kpoints_abs and explicit_kpoints_rel.
          Empty if the point is not a special point.
        - ``explicit_kpoints_linearcoord``: array of floats, giving the coordinate
          at which to plot the corresponding point.
        - ``explicit_segments``: a list of length-2 tuples, with the start and end
          index of each segment. **Note**! The indices are supposed to be
          used as follows: the labels for the i-th segment are given by::

            segment_indices = explicit_segments[i]
            segment_labels = explicit_kpoints_labels[slice(*segment_indices)]

          This means, in particular, that if you want the label of the start
          and end points, you should do::

            start_label = explicit_kpoints_labels[segment_indices[0]]
            stop_label = explicit_kpoints_labels[segment_indices[1]-1]

          (note the minus one!)

          Also, note that if
          ``explicit_segments[i-1][1] == explicit_segments[i][0] + 1`` it means
          that the point was calculated only once, and it belongs to both
          paths. Instead, if
          ``explicit_segments[i-1][1] == explicit_segments[i][0]``, then
          this is a 'break' point in the path (e.g., ``explicit_segments[i-1][1]``
          is the X point, and ``explicit_segments[i][0]`` is the R point,
          and typically in a graphical representation they are shown at the
          same coordinate, with a label ``R|X``).
    """
    if recipe == "hpkot":
        from . import hpkot

        res = hpkot.get_path(
            structure=structure,
            with_time_reversal=with_time_reversal,
            threshold=threshold,
            symprec=symprec,
            angle_tolerance=angle_tolerance,
        )

    else:
        raise ValueError(
            "value for 'recipe' not recognized. The only value "
            "currently accepted is 'hpkot'."
        )

    explicit_res = get_explicit_from_implicit(
        res, reference_distance=reference_distance
    )
    for k, v in explicit_res.items():
        res["explicit_{}".format(k)] = v
    return res


def get_path_orig_cell(
    structure,
    with_time_reversal=True,
    recipe="hpkot",
    threshold=1.0e-7,
    symprec=1e-05,
    angle_tolerance=-1.0,
):
    r"""
    Return the kpoint path information for band structure given a
    crystal structure, using the paths from the chosen recipe/reference.
    The original unit cell (i.e., the one provided in input by the user) is used.
    Standardization or symmetrization of the input unit cell is not performed.

    If the provided unit cell is a supercell of a smaller primitive cell,
    return the standard k path of the smaller primitive cell in the basis
    of the supercell reciprocal lattice vectors. In this case, the k-point
    labels lose their meaning as the corresponding k-points are not at the
    high-symmetry points of the first BZ of the given supercell. A
    :py:exc:`~seekpath.SupercellWarning` is issued.

    If you use this module, please cite the paper of the corresponding
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: ``(cell, positions, numbers)``, where
        (if N is the number of atoms):

        - ``cell`` is a :math:`3 \times 3` list of floats (``cell[0]`` is the first lattice
          vector, ...)
        - ``positions`` is a :math:`N \times 3` list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - ``numbers`` is a length-:math:`N` list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

    :param with_time_reversal: if False, and the group has no inversion
        symmetry, additional lines are returned as described in the HPKOT
        paper.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:

       - ``hpkot``: HPKOT paper:
         Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure
         diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
         DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in
        and edge case (e.g., a tetragonal cell, but ``a==c``). For instance,
        in the tI lattice, if ``abs(a-c) < threshold``, a
        :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued.
        Note that depending on the bravais lattice, the meaning of the
        threshold is different (angle, length, ...)

    :param symprec: the symmetry precision used internally by SPGLIB

    :param angle_tolerance: the angle_tolerance used internally by SPGLIB


    :return: a dictionary with the following
      keys:

        - ``point_coords``: a dictionary with label -> float coordinates
        - ``path``: a list of length-2 tuples, with the labels of the starting
          and ending point of each label section
          input crystal structure has inversion symmetry or not.
        - ``augmented_path``: if True, it means that the path was
          augmented with the :math:`-k` points (this happens if both
          has_inversion_symmetry is False, and the user set
          with_time_reversal=False in the input)
        - ``is_supercell``: True if the input unit cell is a supercell of
          a smaller primitive cell.

    :note: An :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued for
        edge cases (e.g. if ``a==b==c`` for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """

    res = get_path(
        structure=structure,
        with_time_reversal=with_time_reversal,
        threshold=threshold,
        symprec=symprec,
        angle_tolerance=angle_tolerance,
        recipe=recipe,
    )

    is_supercell = abs(res["volume_original_wrt_prim"] - 1) > 0.1

    if is_supercell:
        warnings.warn(
            "The provided cell is a supercell: the returned k-path is the "
            "standard k-path of the associated primitive cell in the basis of "
            "the supercell reciprocal lattice.",
            SupercellWarning,
        )

    # points in the output of get_path are in scaled coordinates of the
    # standardized primitive lattice
    points_scaled_standard = res["point_coords"]

    # Convert points from scaled coordinates of the standardiced primitive
    # lattice to Cartesian coordinates
    points_cartesian = {}
    for pointname, coords in points_scaled_standard.items():
        points_cartesian[pointname] = coords @ np.array(
            res["reciprocal_primitive_lattice"]
        )

    # Rotate points in Cartesian space
    for pointname, coords in points_cartesian.items():
        points_cartesian[pointname] = coords @ res["rotation_matrix"]

    # Convert points from Cartesian coordinates to the scaled coordinates
    # of the original lattice
    points_scaled_original = {}
    cell_orig = np.array(structure[0])
    for pointname, coords in points_cartesian.items():
        points_scaled_original[pointname] = list(coords @ cell_orig.T / np.pi / 2)

    res_orig = {
        "point_coords": points_scaled_original,
        "path": res["path"],
        "augmented_path": res["augmented_path"],
        "is_supercell": is_supercell,
        "has_inversion_symmetry": res["has_inversion_symmetry"],
        "bravais_lattice": res["bravais_lattice"],
        "bravais_lattice_extended": res["bravais_lattice_extended"],
        "spacegroup_number": res["spacegroup_number"],
        "spacegroup_international": res["spacegroup_international"],
    }

    return res_orig


def get_explicit_k_path_orig_cell(
    structure,
    with_time_reversal=True,
    reference_distance=0.025,
    recipe="hpkot",
    threshold=1.0e-7,
    symprec=1e-05,
    angle_tolerance=-1.0,
):
    r"""
    Return the kpoint path for band structure (in scaled and absolute
    coordinates), given a crystal structure,
    using the paths proposed in the various publications (see description
    of the 'recipe' input parameter) for the given unit cell.
    Standardization or symmetrization of the input unit cell is not performed.

    If the provided unit cell is a supercell of a smaller primitive cell,
    return the standard k path of the smaller primitive cell in the basis
    of the supercell reciprocal lattice vectors. In this case, the k-point
    labels lose their meaning as the corresponding k-points are not at the
    high-symmetry points of the first BZ of the given supercell. A
    :py:exc:`~seekpath.SupercellWarning` is issued.

    If you use this module, please cite the paper of the corresponding
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: (cell, positions, numbers), where
        (if N is the number of atoms):

        - ``cell`` is a :math:`3 \times 3` list of floats (``cell[0]`` is the first lattice
          vector, ...)
        - ``positions`` is a :math:`N \times 3` list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - ``numbers`` is a length-:math:`N` list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

    :param with_time_reversal: if False, and the group has no inversion
        symmetry, additional lines are returned.

    :param reference_distance: a reference target distance between neighboring
        k-points in the path, in units of 1/ang. The actual value will be as
        close as possible to this value, to have an integer number of points in
        each path.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:

       - ``hpkot``: HPKOT paper:
         Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure
         diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
         DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in
        and edge case (e.g., a tetragonal cell, but ``a==c``). For instance,
        in the tI lattice, if ``abs(a-c) < threshold``, a
        :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued.
        Note that depending on the bravais lattice, the meaning of the
        threshold is different (angle, length, ...)

    :param symprec: the symmetry precision used internally by SPGLIB

    :param angle_tolerance: the angle_tolerance used internally by SPGLIB

    .. versionchanged:: 1.8
        The key ``segments`` has been renamed ``explicit_segments``
        for consistency.

    :return: a dictionary with a number of keys. They are the same as
        ``get_path_orig_cell``, plus a few ones:

        - ``explicit_kpoints_abs``: List of the kpoints along the specific path in
          absolute (Cartesian) coordinates. The two endpoints are always
          included, independently of the length.
        - ``explicit_kpoints_rel``: List of the kpoints along the specific path in
          relative (fractional) coordinates (same length as
          explicit_kpoints_abs).
        - ``explicit_kpoints_labels``: list of strings with kpoints labels. It has
          the same length as explicit_kpoints_abs and explicit_kpoints_rel.
          Empty if the point is not a special point.
        - ``explicit_kpoints_linearcoord``: array of floats, giving the coordinate
          at which to plot the corresponding point.
        - ``explicit_segments``: a list of length-2 tuples, with the start and end
          index of each segment. **Note**! The indices are supposed to be
          used as follows: the labels for the i-th segment are given by::

            segment_indices = explicit_segments[i]
            segment_labels = explicit_kpoints_labels[slice(*segment_indices)]

          This means, in particular, that if you want the label of the start
          and end points, you should do::

            start_label = explicit_kpoints_labels[segment_indices[0]]
            stop_label = explicit_kpoints_labels[segment_indices[1]-1]

          (note the minus one!)

          Also, note that if
          ``explicit_segments[i-1][1] == explicit_segments[i][0] + 1`` it means
          that the point was calculated only once, and it belongs to both
          paths. Instead, if
          ``explicit_segments[i-1][1] == explicit_segments[i][0]``, then
          this is a 'break' point in the path (e.g., ``explicit_segments[i-1][1]``
          is the X point, and ``explicit_segments[i][0]`` is the R point,
          and typically in a graphical representation they are shown at the
          same coordinate, with a label ``R|X``).
    """
    from .hpkot.tools import get_reciprocal_cell_rows

    res = get_path_orig_cell(
        structure=structure,
        with_time_reversal=with_time_reversal,
        threshold=threshold,
        symprec=symprec,
        angle_tolerance=angle_tolerance,
        recipe=recipe,
    )

    # Set reciprocal_primitive_lattice as the reciprocal lattice of the original
    # cell. To be used only in the get_explicit_from_implicit function.
    res["reciprocal_primitive_lattice"] = get_reciprocal_cell_rows(structure[0])

    explicit_res = get_explicit_from_implicit(
        res, reference_distance=reference_distance
    )

    res.pop("reciprocal_primitive_lattice")

    for k, v in explicit_res.items():
        res["explicit_{}".format(k)] = v
    return res
