def get_path(structure):
    """
    Return the kpoint path for band structure given a crystal structure,
    using the paths proposed in the HKOT paper: 
    Y. Hinuma, Y Kumagai, F. Oba, I. Tanaka, Band structure diagram 
    paths based on crystallography, arXiv:XXXXXXXX

    If you use this module, please cite both the above paper, and the
    AiiDA paper (G. Pizzi et al., Comp. Mat. Sci. 111, 218 (2016))

    # TODO: write full reference

    # TODO: implement edge cases
    # TODO: implement other cases
    # TODO: implement inversion symmetry
    # I assume here structure is an ase structure, but this can be changed
    # Use probably 1.9.3 and fix the check_spglib_version

    # TO DISCUSS: PUT _1 instead of simply 1?
    # TO DISCUSS: examples of structure for each case?
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
        raise NotImplementedError
    elif label == "cF":
        raise NotImplementedError
    elif label == "cI":
        case = "cI1"
    elif label == "tP":
        case = "tP1"
    elif label == "tI":
        raise NotImplementedError
    elif label == "oP":
        case = "oP1"
    elif label == "oF":
        raise NotImplementedError
    elif label == "oI":
        raise NotImplementedError
    elif label == "oC":
        raise NotImplementedError
    elif label == "oA":
        raise NotImplementedError
    elif label == "hP":
        raise NotImplementedError
    elif label == "hR":
        raise NotImplementedError
    elif label == "mP":
        case = "mP1"
    elif label == "mC":
        if b < a * sqrt(1-cosbeta**2):
            case = "mC1"
        else:
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

