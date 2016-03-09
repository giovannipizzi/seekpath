from spg_mapping import get_spgroup_data

def eval_expr_simple(expr,kparam):
    """
    To evaluate expressions tha only require kparams and not a,b,c,...
    """
    if expr == "0":
        return 0.
    elif expr == "1/2":
        return 1./2.
    elif expr == "-1/2":
        return -1./2.
    else:
        try:
            return kparam[expr]
        except KeyError as e:
            raise ValueError("Asking for evaluation of symbol '{}' in eval_expr_simple but this has not been defined or not yet computed".format(e.message))

def extend_kparam(kparam):
    """
    extend the list of kparam with also expressions like 1-x, ...
    """
    kparam_extended = {}
    for k, v in kparam.iteritems():
        kparam_extended[k] = v
        kparam_extended["-{}".format(k)] = -v
        kparam_extended["1-{}".format(k)] = 1.-v
        kparam_extended["-1+{}".format(k)] = -1.+v

    return kparam_extended

def eval_expr(expr,a,b,c,cosalpha,cosbeta,cosgamma,kparam):
    """
    To evaluate expressions, I hardcode a table of existing expressions in the
    DB rather than parsing the string.
    """
    from math import sqrt
    sinalpha = sqrt(1.-cosalpha**2)
    sinbeta = sqrt(1.-cosbeta**2)
    singamma = sqrt(1.-cosgamma**2)
    
    try:
        if expr == "(a*a/b/b+(1+a/c*cosbeta)/sinbeta/sinbeta)/4":
            return (a*a/b/b+(1.+a/c*cosbeta)/sinbeta/sinbeta)/4.
        elif expr == "1-Z*b*b/a/a":
            Z = kparam['Z']
            return 1.-Z*b*b/a/a
        elif expr == "1/2-2*Z*c*cosbeta/a":
            Z = kparam['Z']
            return 1./2.-2.*Z*c*cosbeta/a
        elif expr == "E/2+a*a/4/b/b+a*c*cosbeta/2/b/b":
            E = kparam['E']
            return E/2.+a*a/4./b/b+a*c*cosbeta/2./b/b
        elif expr == "2*F-Z":
            F = kparam['F']
            Z = kparam['Z']
            return 2.*F-Z
        elif expr == "c/2/a/cosbeta*(1-4*U+a*a*sinbeta*sinbeta/b/b)":
            U = kparam['U']            
            return c/2./a/cosbeta*(1.-4.*U+a*a*sinbeta*sinbeta/b/b)
        elif expr == "-1/4+W/2-Z*c*cosbeta/a":
            W = kparam['W']            
            Z = kparam['Z']                        
            return -1./4.+W/2.-Z*c*cosbeta/a
        else:
            raise ValueError('Unknown expression, define a new case:\n'
                            '        elif expr == "{0}":\n'
                            '            return {0}'.format(expr))
    except KeyError as e:
        raise ValueError("Asking for evaluation of symbol '{}' but this has not been defined or not yet computed".format(e.message))

def check_spglib_version(spglib_module):
    try:
        version = spglib.__version__
    except NameError:
        version = "1.8.0" # or older, version was introduced only recently

    try:
        version_pieces = [int(_) for _ in version.split('.')]
        if len(version_pieces) < 3:
            raise ValueError
    except ValueError:
        raise ValueError("Unable to parse version number")

    if tuple(version[:2]) < (1,9):
        raise ValueError("Invalid spglib version, need >= 1.9.0")

def get_cell_params(cell):
    """
    return (a,b,c,cosalpha,cosbeta,cosgamma) given a 3x3 cell
    (rows are vectors)
    """
    import numpy
    from math import sqrt
    
    v1, v2, v3 = cell
    a = sqrt(sum(v1**2))
    b = sqrt(sum(v2**2))
    c = sqrt(sum(v3**2))
    cosalpha = numpy.dot(v2,v3)/b/c
    cosbeta  = numpy.dot(v1,v3)/a/c
    cosgamma = numpy.dot(v1,v2)/a/b
    
    return (a,b,c,cosalpha,cosbeta,cosgamma)
    
def get_path(structure):
    """
    Return the kpoint path for band structure given a crystal structure
    # TODO: implement edge cases
    # TODO: implement other cases
    # TODO: implement inversion symmetry

    # TO DISCUSS: PUT _1 instead of simply 1?
    # TO DISCUSS: examples of structure for each case?
    """
    from math import sqrt
    import spglib
    import os
    
    # I assume here structure is an ase structure, but this can be changed
    check_spglib_version(spglib)

    dataset = spglib.get_symmetry_dataset(structure)
    std_cell = dataset['std_lattice']
    a,b,c,cosalpha,cosbeta,cosgamma=get_cell_params(dataset['std_lattice'])
    spgrp_num = dataset['number']

    properties = get_spgroup_data()[spgrp_num]

    label = "{}{}".format(properties[0], properties[1])
    has_inv = properties[2]

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
            if -a * cosbeta / c + a**2 * (1 - cosbeta**2) / b**2 < 1.: # 12-face
                case = "mC2"
            else:
                case = "mC3"
    elif label == "aP":
        case = "aP1"
    else:
        raise ValueError("Unknown type '{}' for spgrp {}".format(
            label, dataset['number']))

    folder = os.path.join("band_data",case)
    path_file = os.path.join(folder,"path.txt")
    points_file = os.path.join(folder,"points.txt")
    kparam_file = os.path.join(folder,"k_vector_parameter.txt")

    with open(kparam_file) as f:
        kparam_raw = [_.split('=') for _ in f.readlines()]
    with open(points_file) as f:
        points_raw = [_.split() for _ in f.readlines()]
    with open(path_file) as f:
        path_raw = [_.split() for _ in f.readlines()]
    # check
    if any(len(_) != 2 for _ in kparam_raw):
        raise ValueError("Invalid line length in {}".format(kparam_file))
    if any(len(_) != 2 for _ in path_raw):
        raise ValueError("Invalid line length in {}".format(path_file))
    if any(len(_) != 4 for _ in points_raw):
        raise ValueError("Invalid line length in {}".format(points_file))
    # orde must be preserved here
    kparam_def = [(_[0], _[1].strip()) for _ in kparam_raw] 
    points_def = {_[0]: (_[1], _[2], _[3]) for _ in points_raw}
    path = [(_[0], _[1]) for _ in path_raw]
    
    kparam = {}
    for kparam_name, kparam_expr in kparam_def:
        kparam[kparam_name] = eval_expr(kparam_expr,
                                        a,b,c,cosalpha,cosbeta,cosgamma,
                                        kparam)     

    kparam_extended = extend_kparam(kparam)
        
    points = {}
    for pointname, coords_def in points_def.iteritems():
        coords = [eval_expr_simple(_, kparam_extended) for _ in coords_def]
        points[pointname] = coords

    # check path is valid
    for p1, p2 in path:
        if p1 not in points:
            raise ValueError("Point {} found in path but undefined!".format(p1))
        if p2 not in points:
            raise ValueError("Point {} found in path but undefined!".format(p2))
        
    return {'point_coords': points,
            'path': path}

    
    

if __name__ == "__main__":
    import ase
    # spgrp 12, mC, invsym: [12, 15]
    #b > a * sqrt(1-cosbeta**2)
    #-a * cosbeta / c + a**2 * (1 - cosbeta**2) / b**2 > 1

    s = ase.Atoms('C2O8', cell=[[3,0,0],[0,2,0],[-1,0,0.8]])
    s.set_scaled_positions(
        [
            [0,0,0],
            [0.5,0.5,0],
            [0.1,0.2,0.3],
            [-0.1,0.2,-0.3],
            [-0.1,-0.2,-0.3],
            [0.1,-0.2,0.3],
            [0.6,0.7,0.3],
            [-0.6,0.7,-0.3],
            [-0.6,-0.7,-0.3],
            [0.6,-0.7,0.3],
        ])
    print get_path(s)
