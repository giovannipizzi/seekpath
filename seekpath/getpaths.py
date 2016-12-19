"""
This module contains the main functions to get a path and an explicit path.
"""
from builtins import range


def get_path(structure, with_time_reversal=True, recipe='hpkot',
             threshold=1.e-7):
    """
    Return the kpoint path information for band structure given a 
    crystal structure, using the paths from the chosen recipe/reference.

    If you use this module, please cite the paper of the corresponding 
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: (cell, positions, numbers), where 
        (if N is the number of atoms):

        - cell is a 3x3 list of floats (cell[0] is the first lattice 
          vector, ...)
        - positions is a Nx3 list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - numbers is a length-N list with integers identifying uniquely
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
       'hpkot': HPKOT paper: 
       Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure 
       diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
       DOI: 10.1016/j.commatsci.2016.10.015

   :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI lattice, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
        Note that depending on the bravais lattice, the meaning of the 
        threshold is different (angle, length, ...)

    :return: a dictionary with the following 
      keys:

        - point_coords: a dictionary with label -> float coordinates
        - path: a list of length-2 tuples, with the labels of the starting
          and ending point of each label section
        - has_inversion_symmetry: True or False, depending on whether the
          input crystal structure has inversion symmetry or not.
        - augmented_path: if True, it means that the path was
          augmented with the -k points (this happens if both 
          has_inversion_symmetry is False, and the user set 
          with_time_reversal=False in the input)
        - bravais_lattice: the Bravais lattice string (like 'cP', 'tI', ...)
        - bravais_lattice_extended: the specific case used to define labels and
          coordinates (like 'cP1', 'tI2', ...)
        - cont_lattice: three real-space vectors for the crystallographic
          conventional cell (conv_lattice[0,:] is the first vector)
        - conv_positions: fractional coordinates of atoms in the 
          crystallographic conventional cell 
        - conv_types: list of integer types of the atoms in the crystallographic
          conventional cell (typically, the atomic numbers)
        - primitive_lattice: three real-space vectors for the crystallographic 
          primitive cell (primitive_lattice[0,:] is the first vector)
        - primitive_positions: fractional coordinates of atoms in the 
          crystallographic primitive cell 
        - primitive_types: list of integer types of the atoms in the 
          crystallographic primitive cell (typically, the atomic numbers)
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - primitive_transformation_matrix: the transformation matrix P between
          the conventional and the primitive cell 
        - inverse_primitive_transformation_matrix: the inverse of the matrix P
          (the determinant is integer and gives the ratio in volume between
          the conventional and primitive cells)
        - volume_original_wrt_conv: volume ratio of the user-provided cell
          with respect to the the crystallographic conventional cell 
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the crystalloraphic primitive cell 

    :note: An EdgeCaseWarning is issued for edge cases (e.g. if a==b==c for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    if recipe == 'hpkot':
        from . import hpkot
        res = hpkot.get_path(structure, with_time_reversal, threshold)

        return res
    else:
        raise ValueError("value for 'recipe' not recognized. The only value "
                         "currently accepted is 'hpkot'.")


def get_explicit_k_path(structure, with_time_reversal=True,
                        reference_distance=0.025, recipe='hpkot',
                        threshold=1.e-7):
    """
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

        - cell is a 3x3 list of floats (cell[0] is the first lattice 
          vector, ...)
        - positions is a Nx3 list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - numbers is a length-N list with integers identifying uniquely
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
       'hpkot': HPKOT paper: 
       Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure 
       diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
       DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI lattice, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
        Note that depending on the bravais lattice, the meaning of the 
        threshold is different (angle, length, ...)

    :return: a dictionary with the following 
        keys:

        - has_inversion_symmetry: True or False, depending on whether the
          input crystal structure has inversion symmetry or not.
        - augmented_path: if True, it means that the path was
          augmented with the -k points (this happens if both 
          has_inversion_symmetry is False, and the user set 
          with_time_reversal=False in the input)
        - primitive_lattice: three real-space vectors for the crystallographic 
          primitive cell (primitive_lattice[0,:] is the first vector)
        - primitive_positions: fractional coordinates of atoms in the 
          crystallographic primitive cell 
        - primitive_types: list of integer types of the atoms in the 
          crystallographic primitive cell (typically, the atomic numbers)
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the crystallographic primitive cell 
        - explicit_kpoints_abs: List of the kpoints along the specific path in 
          absolute (Cartesian) coordinates. The two endpoints are always 
          included, independently of the length.
        - explicit_kpoints_rel: List of the kpoints along the specific path in 
          relative (fractional) coordinates (same length as 
          explicit_kpoints_abs).
        - explicit_kpoints_labels: list of strings with kpoints labels. It has 
          the same length as explicit_kpoints_abs and explicit_kpoints_rel. 
          Empty if the point is not a special point.
        - explicit_kpoints_linearcoord: array of floats, giving the coordinate 
          at which to plot the corresponding point.
        - segments: a list of length-2 tuples, with the start and end 
          index of each segment. **Note**! The indices are supposed to be 
          used as follows: the labels for the i-th segment are given by::

            segment_indices = segments[i]
            segment_labels = explicit_kpoints_labels[slice(*segment_indices)]

          This means, in particular, that if you want the label of the start
          and end points, you should do::

            start_label = explicit_kpoints_labels[segment_indices[0]]
            stop_label = explicit_kpoints_labels[segment_indices[1]-1]

          (note the minus one!)

          Also, note that if 
          ``segments[i-1][1] == segments[i][0] + 1`` it means
          that the point was calculated only once, and it belongs to both 
          paths. Instead, if 
          ``segments[i-1][1] == segments[i][0]``, then
          this is a 'break' point in the path (e.g., ``segments[i-1][1]``
          is the X point, and ``segments[i][0]`` is the R point, 
          and typically in a graphical representation they are shown at the 
          same coordinate, with a label "R|X").
    """
    import numpy as np

    if recipe == 'hpkot':
        from . import hpkot
        res = hpkot.get_path(structure, with_time_reversal, threshold)

        retdict = {}
        retdict['has_inversion_symmetry'] = res['has_inversion_symmetry']
        retdict['augmented_path'] = res['augmented_path']
        retdict['primitive_lattice'] = res['primitive_lattice']
        retdict['primitive_positions'] = res['primitive_positions']
        retdict['primitive_types'] = res['primitive_types']
        retdict['reciprocal_primitive_lattice'] = res[
            'reciprocal_primitive_lattice']
        retdict['volume_original_wrt_prim'] = res[
            'volume_original_wrt_prim']

        kpoints_rel = []
        kpoints_labels = []
        kpoints_linearcoord = []
        previous_linearcoord = 0.
        segments = []
        for start_label, stop_label in res['path']:
            start_coord = np.array(res['point_coords'][start_label])
            stop_coord = np.array(res['point_coords'][stop_label])
            start_coord_abs = np.dot(start_coord,
                                     retdict['reciprocal_primitive_lattice'])
            stop_coord_abs = np.dot(stop_coord,
                                    retdict['reciprocal_primitive_lattice'])
            segment_length = np.linalg.norm(stop_coord_abs - start_coord_abs)
            num_points = max(2, int(segment_length / reference_distance))
            segment_linearcoord = np.linspace(0., segment_length, num_points)
            segment_start = len(kpoints_labels)
            for i in range(num_points):
                # Skip the first point if it's the same as the last one of
                # the previous segment
                if i == 0:
                    if kpoints_labels:
                        if kpoints_labels[-1] == start_label:
                            segment_start -= 1
                            continue

                kpoints_rel.append(start_coord +
                                   (stop_coord - start_coord) * float(i) / float(num_points - 1))
                if i == 0:
                    kpoints_labels.append(start_label)
                elif i == num_points - 1:
                    kpoints_labels.append(stop_label)
                else:
                    kpoints_labels.append('')
                kpoints_linearcoord.append(
                    previous_linearcoord + segment_linearcoord[i])
            previous_linearcoord += segment_length
            segment_end = len(kpoints_labels)
            segments.append((segment_start, segment_end))

        retdict['explicit_kpoints_rel'] = np.array(kpoints_rel)
        retdict['explicit_kpoints_linearcoord'] = np.array(kpoints_linearcoord)
        retdict['explicit_kpoints_labels'] = kpoints_labels
        retdict['explicit_kpoints_abs'] = np.dot(
            retdict['explicit_kpoints_rel'],
            retdict['reciprocal_primitive_lattice'])
        retdict['segments'] = segments

        return retdict
    else:
        raise ValueError("value for 'recipe' not recognized. The only value "
                         "currently accepted is 'hpkot'.")
