class EdgeCaseWarning(RuntimeWarning):
    """
    A warning issued when the cell is an edge case (e.g. orthorhombic
    symmetry, but a==b==c.
    """
    pass

def get_path(structure, with_time_reversal=True, threshold=1.e-7):
    """
    Return the kpoint path for band structure given a crystal structure,
    using the paths proposed in the HKOT paper: 
    Y. Hinuma, Y Kumagai, F. Oba, I. Tanaka, Band structure diagram 
    paths based on crystallography, arXiv:1602.06402 (2016)

    If you use this module, please cite both the above paper for the path,
    and the AiiDA paper for the implementation: 
    G. Pizzi et al., Comp. Mat. Sci. 111, 218 (2016).

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
        symmetry, additional lines are returned as described in the HKOT
        paper.

    :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI case, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
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
        - bravais_lattice_case: the specific case used to define labels and
          coordinates (like 'cP1', 'tI2', ...)
 
    TODO ADD new outputs in the docs

    :note: An EdgeCaseWarning is issued for edge cases (e.g. if a==b==c for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    import copy
    from math import sqrt
    import warnings

    import numpy
    
    from .tools import (
        check_spglib_version, extend_kparam, eval_expr, eval_expr_simple, 
        get_cell_params, get_path_data, get_reciprocal_cell_rows)
    from .spg_mapping import (get_spgroup_data, get_primitive)

    # I check if the SPGlib version is recent enough (raises ValueError)
    # otherwise
    spglib = check_spglib_version()

    # Symmetry analysis by SPGlib, get standard lattice, 
    # and cell parameters for this lattice
    dataset = spglib.get_symmetry_dataset(structure)
    std_lattice = dataset['std_lattice']
    std_positions = dataset['std_positions']
    std_types = dataset['std_types']
    a,b,c,cosalpha,cosbeta,cosgamma=get_cell_params(std_lattice)
    spgrp_num = dataset['number']
    # This is the transformation from the original to the standard conventional
    #  Lattice^{standard_bravais} = L^{original} * transf_matrix
    transf_matrix = dataset['transformation_matrix']

    # Get the properties of the spacegroup, needed to get the bravais_lattice
    properties = get_spgroup_data()[spgrp_num]
    bravais_lattice = "{}{}".format(properties[0], properties[1])
    has_inv = properties[2]

    (prim_lattice, prim_pos, prim_types), (P, invP), conv_prim_mapping = get_primitive(
        structure = (std_lattice, std_positions, std_types), 
        bravais_lattice = bravais_lattice)
    ## NOTE: we cannot do this, because the find_primitive of spglib
    ## follows a different convention for mC and oA as explained in the
    ## HKOT paper
    # spglib_primitive = spglib.find_primitive(structure)

    # Implement all different cases
    if bravais_lattice == "cP":
        if spgrp_num >= 195 and spgrp_num <= 206:
            case = "cP1"
        elif spgrp_num >= 207 and spgrp_num <= 230:
            case = "cP2"
        else:
            raise ValueError("Internal error! should be cP, but the "
                "spacegroup number is not in the correct range")
    elif bravais_lattice == "cF":
        if spgrp_num >= 195 and spgrp_num <= 206:
            case = "cF1"
        elif spgrp_num >= 207 and spgrp_num <= 230:
            case = "cF2"
        else:
            raise ValueError("Internal error! should be cF, but the "
                "spacegroup number is not in the correct range")
    elif bravais_lattice == "cI":
        case = "cI1"
    elif bravais_lattice == "tP":
        case = "tP1"
    elif bravais_lattice == "tI":
        if abs(c-a) < threshold:
            warnings.warn("tI case, but a almost equal to c",
                EdgeCaseWarning)
        if c <= a:
            case = "tI1"
        else:
            case = "tI2"
    elif bravais_lattice == "oP":
        case = "oP1"
    elif bravais_lattice == "oF":
        if abs(1./(a**2) - (1./(b**2) + 1./(c**2))) < threshold:
            warnings.warn("oF case, but 1/a^2 almost equal to 1/b^2 + 1/c^2",
                EdgeCaseWarning)
        if abs(1./(c**2) - (1./(a**2) + 1./(b**2))) < threshold:
            warnings.warn("oF case, but 1/c^2 almost equal to 1/a^2 + 1/b^2",
                EdgeCaseWarning)
        if 1./(a**2) > 1./(b**2) + 1./(c**2):
            case = "oF1"
        elif 1./(c**2) > 1./(a**2) + 1./(b**2):
            case = "oF2"
        else: # 1/a^2, 1/b^2, 1/c^2 edges of a triangle
            case = "oF3"
    elif bravais_lattice == "oI":
        # Sort a,b,c, first is the largest
        sorted_vectors = sorted([(c,1,'c'),(b,3,'b'),(a,2,'a')])[::-1]
        if abs(sorted_vectors[0][0] - sorted_vectors[1][0]) < threshold:
            warnings.warn("oI case, but the two longest vectors {} and {} "
                "have almost the same length".format(
                    sorted_vectors[0][2], sorted_vectors[1][2]),
                EdgeCaseWarning)            
        case = "{}{}".format(bravais_lattice, sorted_vectors[0][1])
    elif bravais_lattice == "oC":
        if abs(b-a) < threshold:
            warnings.warn("oC case, but a almost equal to b",
                EdgeCaseWarning)
        if a <= b:
            case = "oC1"
        else:
            case = "oC2"
    elif bravais_lattice == "oA":
        if abs(b-c) < threshold:
            warnings.warn("oA case, but b almost equal to c",
                EdgeCaseWarning)
        if b <= c:
            case = "oA1"
        else:
            case = "oA2"
    elif bravais_lattice == "hP":
        if spgrp_num in [143, 144, 145, 146, 147, 148, 149, 151, 153, 157, 
            159, 160, 161, 162, 163]:
            case = "hP1"
        else:
            case = "hP2"
    elif bravais_lattice == "hR":
        if abs(sqrt(3.) * a - sqrt(2.) * c) < threshold:
            warnings.warn("hR case, but sqrt(3)a almost equal to sqrt(2)c",
                EdgeCaseWarning)        
        if sqrt(3.) * a <= sqrt(2.) * c:
            case = "hR1"
        else:
            case = "hR2"
    elif bravais_lattice == "mP":
        case = "mP1"
    elif bravais_lattice == "mC":
        if abs(b - a * sqrt(1.-cosbeta**2)) < threshold:
            warnings.warn("mC case, but b almost equal to a*sin(beta)",
                EdgeCaseWarning)                    
        if b < a * sqrt(1.-cosbeta**2):
            case = "mC1"
        else:
            if abs(-a * cosbeta / c + a**2 * (1. - cosbeta**2) / b**2 
                   - 1.) < threshold:
                warnings.warn("mC case, but -a*cos(beta)/c + "
                    "a^2*sin(beta)^2/b^2 almost equal to 1",
                    EdgeCaseWarning)                    
            if -a * cosbeta / c + a**2 * (1. - cosbeta**2) / b**2 <= 1.: 
                # 12-face
                case = "mC2"
            else:
                case = "mC3"
    elif bravais_lattice == "aP":
        reciprocal_cell = get_reciprocal_cell_rows(std_lattice)

        # I use the default eps here, this could be changed
        niggli_rec_cell = spglib.niggli_reduce(reciprocal_cell)
        # TODO: get transformation matrix?

        ka,kb,kc,coskalpha,coskbeta,coskgamma=get_cell_params(
            niggli_rec_cell)   

        if abs(coskalpha) < threshold:
            warnings.warn("aP case, but the k_alpha angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)                    
        if abs(coskbeta) < threshold:
            warnings.warn("aP case, but the k_beta angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)                    
        if abs(coskgamma) < threshold:
            warnings.warn("aP case, but the k_gamma angle is almost equal "
                "to 90 degrees", EdgeCaseWarning)                    

        if coskalpha <= 0. and coskbeta <= 0. and coskgamma <= 0.:
            # all-obtuse
            case = "aP2"
        elif coskalpha >= 0. and coskbeta >= 0. and coskgamma >= 0.:
            # all-acute
            case = "aP3"
        else:
            raise ValueError("Unexpected aP triclinic case, it neither "
                "all-obtuse nor all-acute! Sign of cosines: cos(kalpha){}0, "
                "cos(kbeta){}0, cos(kgamma){}0".format(
                    ">=" if coskalpha >= 0 else "<",
                    ">=" if coskbeta >= 0 else "<",
                    ">=" if coskgamma >= 0 else "<"))

        raise NotImplementedError("Still to implement: "
            "reordering as explained in "
            "the HKOT paper")
    else:
        raise ValueError("Unknown type '{}' for spgrp {}".format(
            bravais_lattice, dataset['number']))

    # Get the path data (k-parameters definitions, defition of the points,
    # suggested path)
    kparam_def, points_def, path = get_path_data(case)
    
    # Get the actual numerical values of the k-parameters
    # Note: at each step, I pass kparam and store the new
    # parameter in the same dictionary. This allows to have
    # some parameters defined implicitly in terms of previous
    # parameters, as far as they are returned in the 
    kparam = {}
    for kparam_name, kparam_expr in kparam_def:
        kparam[kparam_name] = eval_expr(
            kparam_expr, a, b, c, cosalpha, cosbeta, cosgamma, kparam)

    # Extend kparam with additional simple expressions (like 1-a, ...)
    kparam_extended = extend_kparam(kparam)
        
    # Now I have evaluated all needed kparams; I can compute the actual
    # coordinates of the relevant kpoints, using eval_expr_simple
    points = {}
    for pointname, coords_def in points_def.iteritems():
        coords = [eval_expr_simple(_, kparam_extended) for _ in coords_def]
        points[pointname] = coords

    # If there is no inversion symmetry nor time-reversal symmetry, add
    # additional path
    if not has_inv and not with_time_reversal:
        augmented_path = True
    else:
        augmented_path = False

    if augmented_path:
        for pointname, coords in list(points.iteritems()):
            if pointname == 'GAMMA':
                continue
            points["{}'".format(pointname)] = [
                -coords[0],-coords[1],-coords[2]]
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
            path.append([new_start_p, new_end_p])

    return {'point_coords': points,
            'path': path,
            'has_inversion_symmetry': has_inv,
            'augmented_path': augmented_path,
            'bravais_lattice': bravais_lattice,
            'bravais_lattice_case': case,
            'std_lattice': std_lattice,
            'std_positions': std_positions,
            'std_types': std_types,
            'primitive_lattice': prim_lattice,
            'primitive_positions': prim_pos,
            'primitive_types': prim_types, # to std_
            # The following: between std and primitive, see docstring of 
            # spg_mapping.get_P_matrix
            'inverse_primitive_transformation_matrix': invP, 
            'primitive_transformation_matrix': P, 
            'transformation_matrix': transf_matrix,
            'volume_std_wrt_original': numpy.linalg.det(transf_matrix),
            }

