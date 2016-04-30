def get_path(structure):
    """
    Return the kpoint path for band structure given a crystal structure,
    using the paths proposed in the HKOT paper: 
    Y. Hinuma, Y Kumagai, F. Oba, I. Tanaka, Band structure diagram 
    paths based on crystallography, arXiv:XXXXXXXX

    If you use this module, please cite both the above paper, and the
    AiiDA paper (G. Pizzi et al., Comp. Mat. Sci. 111, 218 (2016))

    # TODO: write full reference

    # TODO: implement inversion symmetry

    # I assume here structure is an ase structure, but this can be changed
    # Use probably 1.9.3 and fix the check_spglib_version

    # TODO: implement edge cases (issue warning!)
    """
    from math import sqrt
    
    import spglib

    from .tools import (
        check_spglib_version, extend_kparam, eval_expr, eval_expr_simple, 
        get_cell_params, get_path_data)
    from .spg_mapping import get_spgroup_data

    # I check if the SPGlib version is recent enough (raises ValueError)
    # otherwise
    check_spglib_version(spglib)

    # Symmetry analysis by SPGlib, get standard lattice, 
    # and cell parameters for this lattice
    dataset = spglib.get_symmetry_dataset(structure)
    std_cell = dataset['std_lattice']
    a,b,c,cosalpha,cosbeta,cosgamma=get_cell_params(dataset['std_lattice'])
    spgrp_num = dataset['number']

    # Get the properties of the spacegroup, needed to get the label
    properties = get_spgroup_data()[spgrp_num]
    label = "{}{}".format(properties[0], properties[1])
    has_inv = properties[2]

    # Implement all different cases
    if label == "cP":
        if spgrp_num >= 195 and spgrp <= 206:
            case = "cP1"
        elif spgrp_num >= 207 and spgrp <= 230:
            case = "cP2"
        else:
            raise ValueError("Internal error! should be cP, but the spacegroup "
                "number is not in the correct range")
    elif label == "cF":
        if spgrp_num >= 195 and spgrp <= 206:
            case = "cF1"
        elif spgrp_num >= 207 and spgrp <= 230:
            case = "cF2"
        else:
            raise ValueError("Internal error! should be cP, but the spacegroup "
                "number is not in the correct range")
    elif label == "cI":
        case = "cI1"
    elif label == "tP":
        case = "tP1"
    elif label == "tI":
        if c < a:
            case = "tI1"
        elif c > a:
            case = "tI2"
        else:
            ## TODO WARNING
            case = "tI1"
    elif label == "oP":
        case = "oP1"
    elif label == "oF":
        if 1./(a**2) > 1./(b**2) + 1./(c**2):
            case = "oF1"
        elif 1./(c**2) > 1./(a**2) + 1./(b**2):
            case = "oF2"
        else: # 1/a^2, 1/b^2, 1/c^2 edges of a triangle
            case = "oF3"
    elif label == "oI":
        # Sort a,b,c, first is the largest
        sorted_vectors = sorted([(c,1),(b,3),(a,2)])[::-1]
        case = "{}{}".format(label, sorted_vectors[0][1])
    elif label == "oC":
        if a < b:
            case = "oC1"
        elif a > b:
            case = "oC2"
        else:
            ## TODO WARNING
            case = "oC1"
    elif label == "oA":
        if b < c:
            case = "oA1"
        elif b > c:
            case = "oA2"
        else:
            ## TODO WARNING
            case = "oA1"
    elif label == "hP":
        if spgnum in [143, 144, 145, 146, 147, 148, 149, 151, 153, 157, 
            159, 160, 161, 162, 163]:
            case = "hP1"
        else:
            case = "hP2"
    elif label == "hR":
        if sqrt(3.) * a < sqrt(2.) * c:
            case = "hR1"
        elif sqrt(3.) * a > sqrt(2.) * c:
            case = "hR2"
        else:
            # TODO WARNING
            case = "hR1"
    elif label == "mP":
        case = "mP1"
    elif label == "mC":
        if b < a * sqrt(1-cosbeta**2):
            case = "mC1"
        else:
            # TODO WARNING FOR EDGE CASE
            if -a * cosbeta / c + a**2 * (1 - cosbeta**2) / b**2 < 1.: 
                # 12-face
                case = "mC2"
            else:
                case = "mC3"
    elif label == "aP":
        # I have defined aP2 and aP3 as triclinic all-obtuse and all-acute respectively.
        raise NotImplementedError 
    else:
        raise ValueError("Unknown type '{}' for spgrp {}".format(
            label, dataset['number']))

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
        
    return {'point_coords': points,
            'path': path}

