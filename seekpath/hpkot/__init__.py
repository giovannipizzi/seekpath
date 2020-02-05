"""
The seekpath.hpkot module contains routines to get automatically the
path in a 3D Brillouin zone to plot band structures according to the 
HPKOT paper (see references below).

Author: Giovanni Pizzi, EPFL

Licence: MIT License, see LICENSE.txt

.. note:: the list of point coordinates and example POSCAR files in 
  the band_path_data subfolder have been provided by Yoyo Hinuma,
  Kyoto University, Japan. The POSCARs have been retrieved from
  the Materials Project (http://materialsproject.org).
"""


class EdgeCaseWarning(RuntimeWarning):
    """
    A warning issued when the cell is an edge case (e.g. orthorhombic
    symmetry, but ``a==b==c``.
    """
    pass


class SymmetryDetectionError(Exception):
    """
    Error raised if spglib could not detect the symmetry.
    """
    pass


def get_path(structure,
             with_time_reversal=True,
             threshold=1.e-7,
             symprec=1e-05,
             angle_tolerance=-1.0):
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
          with respect to the the crystallographic primitive cell

    :note: An :py:exc:`~seekpath.hpkot.EdgeCaseWarning` is issued for
        edge cases (e.g. if ``a==b==c`` for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    import copy
    from math import sqrt
    import warnings

    import numpy as np

    from .tools import (check_spglib_version, extend_kparam, eval_expr,
                        eval_expr_simple, get_cell_params, get_path_data,
                        get_reciprocal_cell_rows,
                        get_real_cell_from_reciprocal_rows)
    from .spg_mapping import (get_spgroup_data, get_primitive)

    # I check if the SPGlib version is recent enough (raises ValueError)
    # otherwise
    spglib = check_spglib_version()

    structure_internal = (np.array(structure[0]), np.array(structure[1]),
                          np.array(structure[2]))

    # Symmetry analysis by SPGlib, get crystallographic lattice,
    # and cell parameters for this lattice
    dataset = spglib.get_symmetry_dataset(structure_internal,
                                          symprec=symprec,
                                          angle_tolerance=angle_tolerance)
    if dataset is None:
        raise SymmetryDetectionError(
            "Spglib could not detect the symmetry of the system")
    conv_lattice = dataset['std_lattice']
    conv_positions = dataset['std_positions']
    conv_types = dataset['std_types']
    a, b, c, cosalpha, cosbeta, cosgamma = get_cell_params(conv_lattice)
    spgrp_num = dataset['number']
    # This is the transformation from the original to the crystallographic
    # conventional (called std in spglib)
    #  Lattice^{crystallographic_bravais} = L^{original} * transf_matrix
    transf_matrix = dataset['transformation_matrix']
    volume_conv_wrt_original = np.linalg.det(transf_matrix)

    # Get the properties of the spacegroup, needed to get the bravais_lattice
    properties = get_spgroup_data()[spgrp_num]
    bravais_lattice = "{}{}".format(properties[0], properties[1])
    has_inv = properties[2]

    # Implement all different extended Bravais lattices
    if bravais_lattice == "cP":
        if spgrp_num >= 195 and spgrp_num <= 206:
            ext_bravais = "cP1"
        elif spgrp_num >= 207 and spgrp_num <= 230:
            ext_bravais = "cP2"
        else:
            raise ValueError("Internal error! should be cP, but the "
                             "spacegroup number is not in the correct range")
    elif bravais_lattice == "cF":
        if spgrp_num >= 195 and spgrp_num <= 206:
            ext_bravais = "cF1"
        elif spgrp_num >= 207 and spgrp_num <= 230:
            ext_bravais = "cF2"
        else:
            raise ValueError("Internal error! should be cF, but the "
                             "spacegroup number is not in the correct range")
    elif bravais_lattice == "cI":
        ext_bravais = "cI1"
    elif bravais_lattice == "tP":
        ext_bravais = "tP1"
    elif bravais_lattice == "tI":
        if abs(c - a) < threshold:
            warnings.warn("tI lattice, but a almost equal to c",
                          EdgeCaseWarning)
        if c <= a:
            ext_bravais = "tI1"
        else:
            ext_bravais = "tI2"
    elif bravais_lattice == "oP":
        ext_bravais = "oP1"
    elif bravais_lattice == "oF":
        if abs(1. / (a**2) - (1. / (b**2) + 1. / (c**2))) < threshold:
            warnings.warn("oF lattice, but 1/a^2 almost equal to 1/b^2 + 1/c^2",
                          EdgeCaseWarning)
        if abs(1. / (c**2) - (1. / (a**2) + 1. / (b**2))) < threshold:
            warnings.warn("oF lattice, but 1/c^2 almost equal to 1/a^2 + 1/b^2",
                          EdgeCaseWarning)
        if 1. / (a**2) > 1. / (b**2) + 1. / (c**2):
            ext_bravais = "oF1"
        elif 1. / (c**2) > 1. / (a**2) + 1. / (b**2):
            ext_bravais = "oF2"
        else:  # 1/a^2, 1/b^2, 1/c^2 edges of a triangle
            ext_bravais = "oF3"
    elif bravais_lattice == "oI":
        # Sort a,b,c, first is the largest
        sorted_vectors = sorted([(c, 1, 'c'), (b, 3, 'b'), (a, 2, 'a')])[::-1]
        if abs(sorted_vectors[0][0] - sorted_vectors[1][0]) < threshold:
            warnings.warn(
                "oI lattice, but the two longest vectors {} and {} "
                "have almost the same length".format(sorted_vectors[0][2],
                                                     sorted_vectors[1][2]),
                EdgeCaseWarning)
        ext_bravais = "{}{}".format(bravais_lattice, sorted_vectors[0][1])
    elif bravais_lattice == "oC":
        if abs(b - a) < threshold:
            warnings.warn("oC lattice, but a almost equal to b",
                          EdgeCaseWarning)
        if a <= b:
            ext_bravais = "oC1"
        else:
            ext_bravais = "oC2"
    elif bravais_lattice == "oA":
        if abs(b - c) < threshold:
            warnings.warn("oA lattice, but b almost equal to c",
                          EdgeCaseWarning)
        if b <= c:
            ext_bravais = "oA1"
        else:
            ext_bravais = "oA2"
    elif bravais_lattice == "hP":
        if spgrp_num in [
                143, 144, 145, 146, 147, 148, 149, 151, 153, 157, 159, 160, 161,
                162, 163
        ]:
            ext_bravais = "hP1"
        else:
            ext_bravais = "hP2"
    elif bravais_lattice == "hR":
        if abs(sqrt(3.) * a - sqrt(2.) * c) < threshold:
            warnings.warn("hR lattice, but sqrt(3)a almost equal to sqrt(2)c",
                          EdgeCaseWarning)
        if sqrt(3.) * a <= sqrt(2.) * c:
            ext_bravais = "hR1"
        else:
            ext_bravais = "hR2"
    elif bravais_lattice == "mP":
        ext_bravais = "mP1"
    elif bravais_lattice == "mC":
        if abs(b - a * sqrt(1. - cosbeta**2)) < threshold:
            warnings.warn("mC lattice, but b almost equal to a*sin(beta)",
                          EdgeCaseWarning)
        if b < a * sqrt(1. - cosbeta**2):
            ext_bravais = "mC1"
        else:
            if abs(-a * cosbeta / c + a**2 *
                   (1. - cosbeta**2) / b**2 - 1.) < threshold:
                warnings.warn(
                    "mC lattice, but -a*cos(beta)/c + "
                    "a^2*sin(beta)^2/b^2 almost equal to 1", EdgeCaseWarning)
            if -a * cosbeta / c + a**2 * (1. - cosbeta**2) / b**2 <= 1.:
                # 12-face
                ext_bravais = "mC2"
            else:
                ext_bravais = "mC3"
    elif bravais_lattice == "aP":
        # First step: cell that is Niggli reduced in reciprocal space
        # I use the default eps here, this could be changed
        reciprocal_cell_orig = get_reciprocal_cell_rows(conv_lattice)
        ## This is Niggli-reduced
        reciprocal_cell2 = spglib.niggli_reduce(reciprocal_cell_orig)
        real_cell2 = get_real_cell_from_reciprocal_rows(reciprocal_cell2)
        # TODO: get transformation matrix?

        ka2, kb2, kc2, coskalpha2, coskbeta2, coskgamma2 = get_cell_params(
            reciprocal_cell2)

        conditions = np.array([
            abs(kb2 * kc2 * coskalpha2),
            abs(kc2 * ka2 * coskbeta2),
            abs(ka2 * kb2 * coskgamma2)
        ])
        M2_matrices = [
            np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]]),
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]]),
            np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        ]
        # TODO: manage edge cases
        smallest_condition = np.argsort(conditions)[0]
        M2 = M2_matrices[smallest_condition]
        # First change of vectors to have |ka3 kb3 cosgamma3| smallest
        real_cell3 = np.dot(np.array(real_cell2).T, M2).T
        reciprocal_cell3 = get_reciprocal_cell_rows(real_cell3)
        ka3, kb3, kc3, coskalpha3, coskbeta3, coskgamma3 = get_cell_params(
            reciprocal_cell3)
        if abs(coskalpha3) < threshold:
            warnings.warn(
                "aP lattice, but the k_alpha3 angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)
        if abs(coskbeta3) < threshold:
            warnings.warn(
                "aP lattice, but the k_beta3 angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)
        if abs(coskgamma3) < threshold:
            warnings.warn(
                "aP lattice, but the k_gamma3 angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)
        # Make them all-acute or all-obtuse with the additional conditions
        # explained in HPKOT
        # Note: cos > 0 => angle < 90deg
        if coskalpha3 > 0. and coskbeta3 > 0. and coskgamma3 > 0.:  # 1a
            M3 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        elif coskalpha3 <= 0. and coskbeta3 <= 0. and coskgamma3 <= 0.:  # 1b
            M3 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        elif coskalpha3 > 0. and coskbeta3 <= 0. and coskgamma3 <= 0.:  # 2a
            M3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
        elif coskalpha3 <= 0. and coskbeta3 > 0. and coskgamma3 > 0.:  # 2b
            M3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
        elif coskalpha3 <= 0. and coskbeta3 > 0. and coskgamma3 <= 0.:  # 3a
            M3 = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
        elif coskalpha3 > 0. and coskbeta3 <= 0. and coskgamma3 > 0.:  # 3b
            M3 = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
        elif coskalpha3 <= 0. and coskbeta3 <= 0. and coskgamma3 > 0.:  # 4a
            M3 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
        elif coskalpha3 > 0. and coskbeta3 > 0. and coskgamma3 <= 0.:  # 4b
            M3 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
        else:
            raise ValueError("Problem identifying M3 matrix in aP lattice!"
                             "Sign of cosines: cos(kalpha3){}0, "
                             "cos(kbeta3){}0, cos(kgamma3){}0".format(
                                 ">=" if coskalpha3 >= 0 else "<",
                                 ">=" if coskbeta3 >= 0 else "<",
                                 ">=" if coskgamma3 >= 0 else "<"))

        real_cell_final = np.dot(real_cell3.T, M3).T
        reciprocal_cell_final = get_reciprocal_cell_rows(real_cell_final)
        ka, kb, kc, coskalpha, coskbeta, coskgamma = get_cell_params(
            reciprocal_cell_final)

        if coskalpha <= 0. and coskbeta <= 0. and coskgamma <= 0.:
            # all-obtuse
            ext_bravais = "aP2"
        elif coskalpha >= 0. and coskbeta >= 0. and coskgamma >= 0.:
            # all-acute
            ext_bravais = "aP3"
        else:
            raise ValueError(
                "Unexpected aP triclinic lattice, it neither "
                "all-obtuse nor all-acute! Sign of cosines: cos(kalpha){}0, "
                "cos(kbeta){}0, cos(kgamma){}0".format(
                    ">=" if coskalpha >= 0 else "<",
                    ">=" if coskbeta >= 0 else "<",
                    ">=" if coskgamma >= 0 else "<"))

        # Get absolute positions
        conv_pos_abs = np.dot(conv_positions, conv_lattice)
        # Replace conv_lattice with the new conv_lattice
        conv_lattice = np.array(real_cell_final)
        # Store the relative coords with respect to the new vectors
        # TODO: decide if we want to do %1. for the fractional coordinates
        conv_positions = np.dot(conv_pos_abs, np.linalg.inv(conv_lattice))
        # TODO: implement the correct one (probably we need the matrix
        # out from niggli, and then we can combine it with M2 and M3??)
        # We set it to None for the time being to avoid confusion
        transformation_matrix = None

    else:
        raise ValueError("Unknown type '{}' for spacegroup {}".format(
            bravais_lattice, dataset['number']))

    # NOTE: we simply use spglib.find_primitive, because the
    # find_primitive of spglib follows a different convention for mC
    # and oA as explained in the HPKOT paper
    (prim_lattice, prim_pos, prim_types), (P, invP), conv_prim_mapping = \
        get_primitive(
            structure=(conv_lattice, conv_positions, conv_types),
            bravais_lattice=bravais_lattice)

    # Get the path data (k-parameters definitions, defition of the points,
    # suggested path)
    kparam_def, points_def, path = get_path_data(ext_bravais)

    # Get the actual numerical values of the k-parameters
    # Note: at each step, I pass kparam and store the new
    # parameter in the same dictionary. This allows to have
    # some parameters defined implicitly in terms of previous
    # parameters, as far as they are returned in the
    kparam = {}
    for kparam_name, kparam_expr in kparam_def:
        kparam[kparam_name] = eval_expr(kparam_expr, a, b, c, cosalpha, cosbeta,
                                        cosgamma, kparam)

    # Extend kparam with additional simple expressions (like 1-a, ...)
    kparam_extended = extend_kparam(kparam)

    # Now I have evaluated all needed kparams; I can compute the actual
    # coordinates of the relevant kpoints, using eval_expr_simple
    points = {}
    for pointname, coords_def in points_def.items():
        coords = [eval_expr_simple(_, kparam_extended) for _ in coords_def]
        points[pointname] = coords

    # If there is no inversion symmetry nor time-reversal symmetry, add
    # additional path
    if not has_inv and not with_time_reversal:
        augmented_path = True
    else:
        augmented_path = False

    if augmented_path:
        for pointname, coords in list(points.items()):
            if pointname == 'GAMMA':
                continue
            points["{}'".format(pointname)] = [
                -coords[0], -coords[1], -coords[2]
            ]
        old_path = copy.deepcopy(path)
        for start_p, end_p in old_path:
            if start_p == "GAMMA":
                new_start_p = start_p
            else:
                new_start_p = "{}'".format(start_p)
            if end_p == "GAMMA":
                new_end_p = end_p
            else:
                new_end_p = "{}'".format(end_p)
            path.append((new_start_p, new_end_p))

    return {
        'point_coords':
            points,
        'path':
            path,
        'has_inversion_symmetry':
            has_inv,
        'augmented_path':
            augmented_path,
        'bravais_lattice':
            bravais_lattice,
        'bravais_lattice_extended':
            ext_bravais,
        'conv_lattice':
            conv_lattice,
        'conv_positions':
            conv_positions,
        'conv_types':
            conv_types,
        'primitive_lattice':
            prim_lattice,
        'primitive_positions':
            prim_pos,
        'primitive_types':
            prim_types,
        'reciprocal_primitive_lattice':
            get_reciprocal_cell_rows(prim_lattice),
        # The following: between conv and primitive, see docstring of
        # spg_mapping.get_P_matrix
        'inverse_primitive_transformation_matrix':
            invP,
        'primitive_transformation_matrix':
            P,
        # For the time being disabled, not valid for aP lattices
        # (for which we would need the transformation matrix from niggli)
        #'transformation_matrix': transf_matrix,
        'volume_original_wrt_conv':
            volume_conv_wrt_original,
        'volume_original_wrt_prim':
            volume_conv_wrt_original * np.linalg.det(invP),
        'spacegroup_number':
            dataset['number'],
        'spacegroup_international':
            dataset['international'],
    }
