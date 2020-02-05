import numpy
import numpy.linalg


def eval_expr_simple(expr, kparam):
    """
    To evaluate expressions tha only require kparams and not a, b, c, ...
    """
    if expr == "0":
        return 0.
    elif expr == "1/2":
        return 1. / 2.
    elif expr == "1":
        return 1.
    elif expr == "-1/2":
        return -1. / 2.
    elif expr == "1/4":
        return 1. / 4.
    elif expr == "3/8":
        return 3. / 8.
    elif expr == "3/4":
        return 3. / 4.
    elif expr == "5/8":
        return 5. / 8.
    elif expr == "1/3":
        return 1. / 3.
    else:
        try:
            return kparam[expr]
        except KeyError as e:
            raise ValueError(
                "Asking for evaluation of symbol '{}' in "
                "eval_expr_simple but this has not been defined or not "
                "yet computed".format(e.message))


def extend_kparam(kparam):
    """
    Extend the list of kparam with also expressions like :math:`1-x`, ...

    :param kparam: a dictionary where the key is the expression as a string and
       the value is the numerical value
    :return: a similar dictionary, extended with simple expressions
    """
    kparam_extended = {}
    for k, v in kparam.items():
        kparam_extended[k] = v
        kparam_extended["-{}".format(k)] = -v
        kparam_extended["1-{}".format(k)] = 1. - v
        kparam_extended["-1+{}".format(k)] = -1. + v
        kparam_extended["1/2-{}".format(k)] = 1. / 2. - v
        kparam_extended["1/2+{}".format(k)] = 1. / 2. + v

    return kparam_extended


def eval_expr(expr, a, b, c, cosalpha, cosbeta, cosgamma, kparam):
    r"""
    Given a string expression as a function of the parameters ``a``, ``b``, ``c`` (lengths of the 
    cell lattice vectors) and ``cosalpha``, ``cosbeta``, ``cosgamma`` (the cosines of the three
    angles between lattice vectors) returns the numerical value of the expression.

    :param a: length of the first lattice vector
    :param b: length of the second lattice vector
    :param c: length of the third lattice vector
    :param cosalpha: cosine of the :math:`\alpha` angle (between lattice vectors 2 and 3)
    :param cosbeta: cosine of the :math:`\beta` angle (between lattice vectors 1 and 3)
    :param cosgamma: cosine of the :math:`\gamma` angle (between lattice vectors 1 and 2)
    :param kparam: a dictionary that associates the value to expressions as a function 
        of the ``a, b, c, cosalpha, cosbeta, cosgamma`` parameters

    :return: the value of the expression for the given values of the cell parameters

    .. note::  To evaluate expressions, I hardcode a table of existing expressions in the
        DB rather than parsing the string (to avoid additional dependencies and 
        avoid the use of ``eval``).
    """
    from math import sqrt
    sinalpha = sqrt(1. - cosalpha**2)
    sinbeta = sqrt(1. - cosbeta**2)
    singamma = sqrt(1. - cosgamma**2)

    try:
        if expr == "(a*a/b/b+(1+a/c*cosbeta)/sinbeta/sinbeta)/4":
            return (a * a / b / b +
                    (1. + a / c * cosbeta) / sinbeta / sinbeta) / 4.
        elif expr == "1-Z*b*b/a/a":
            Z = kparam['Z']
            return 1. - Z * b * b / a / a
        elif expr == "1/2-2*Z*c*cosbeta/a":
            Z = kparam['Z']
            return 1. / 2. - 2. * Z * c * cosbeta / a
        elif expr == "E/2+a*a/4/b/b+a*c*cosbeta/2/b/b":
            E = kparam['E']
            return E / 2. + a * a / 4. / b / b + a * c * cosbeta / 2. / b / b
        elif expr == "2*F-Z":
            F = kparam['F']
            Z = kparam['Z']
            return 2. * F - Z
        elif expr == "c/2/a/cosbeta*(1-4*U+a*a*sinbeta*sinbeta/b/b)":
            U = kparam['U']
            return c / 2. / a / cosbeta * (1. - 4. * U +
                                           a * a * sinbeta * sinbeta / b / b)
        elif expr == "-1/4+W/2-Z*c*cosbeta/a":
            W = kparam['W']
            Z = kparam['Z']
            return -1. / 4. + W / 2. - Z * c * cosbeta / a
        elif expr == "(2+a/c*cosbeta)/4/sinbeta/sinbeta":
            return (2. + a / c * cosbeta) / 4. / sinbeta / sinbeta
        elif expr == "3/4-b*b/4/a/a/sinbeta/sinbeta":
            return 3. / 4. - b * b / 4. / a / a / sinbeta / sinbeta
        elif expr == "S-(3/4-S)*a*cosbeta/c":
            S = kparam['S']
            return S - (3. / 4. - S) * a * cosbeta / c
        elif expr == "(1+a*a/b/b)/4":
            return (1. + a * a / b / b) / 4.
        elif expr == "-a*c*cosbeta/2/b/b":
            return -a * c * cosbeta / 2. / b / b
        elif expr == "1+Z-2*M":
            Z = kparam['Z']
            M = kparam['M']
            return 1. + Z - 2. * M
        elif expr == "X-2*D":
            X = kparam['X']
            D = kparam['D']
            return X - 2 * D
        elif expr == "(1+a/c*cosbeta)/2/sinbeta/sinbeta":
            return (1. + a / c * cosbeta) / 2. / sinbeta / sinbeta
        elif expr == "1/2+Y*c*cosbeta/a":
            Y = kparam['Y']
            return 1. / 2. + Y * c * cosbeta / a
        elif expr == "a*a/4/c/c":
            return a * a / 4. / c / c
        elif expr == "5/6-2*D":
            D = kparam['D']
            return 5. / 6. - 2. * D
        elif expr == "1/3+D":
            D = kparam['D']
            return 1. / 3. + D
        elif expr == "1/6-c*c/9/a/a":
            return 1. / 6. - c * c / 9. / a / a
        elif expr == "1/2-2*Z":
            Z = kparam['Z']
            return 1. / 2. - 2. * Z
        elif expr == "1/2+Z":
            Z = kparam['Z']
            return 1. / 2. + Z
        elif expr == "(1+b*b/c/c)/4":
            return (1. + b * b / c / c) / 4.
        elif expr == "(1+c*c/b/b)/4":
            return (1. + c * c / b / b) / 4.
        elif expr == "(1+b*b/a/a)/4":
            return (1. + b * b / a / a) / 4.
        elif expr == "(1+a*a/b/b-a*a/c/c)/4":
            return (1. + a * a / b / b - a * a / c / c) / 4.
        elif expr == "(1+a*a/b/b+a*a/c/c)/4":
            return (1. + a * a / b / b + a * a / c / c) / 4.
        elif expr == "(1+c*c/a/a-c*c/b/b)/4":
            return (1. + c * c / a / a - c * c / b / b) / 4.
        elif expr == "(1+c*c/a/a+c*c/b/b)/4":
            return (1. + c * c / a / a + c * c / b / b) / 4.
        elif expr == "(1+b*b/a/a-b*b/c/c)/4":
            return (1. + b * b / a / a - b * b / c / c) / 4.
        elif expr == "(1+c*c/b/b-c*c/a/a)/4":
            return (1. + c * c / b / b - c * c / a / a) / 4.
        elif expr == "(1+a*a/c/c)/4":
            return (1. + a * a / c / c) / 4.
        elif expr == "(b*b-a*a)/4/c/c":
            return (b * b - a * a) / 4. / c / c
        elif expr == "(a*a+b*b)/4/c/c":
            return (a * a + b * b) / 4. / c / c
        elif expr == "(1+c*c/a/a)/4":
            return (1. + c * c / a / a) / 4.
        elif expr == "(c*c-b*b)/4/a/a":
            return (c * c - b * b) / 4. / a / a
        elif expr == "(b*b+c*c)/4/a/a":
            return (b * b + c * c) / 4. / a / a
        elif expr == "(a*a-c*c)/4/b/b":
            return (a * a - c * c) / 4. / b / b
        elif expr == "(c*c+a*a)/4/b/b":
            return (c * c + a * a) / 4. / b / b
        elif expr == "a*a/2/c/c":
            return a * a / 2. / c / c
        else:
            raise ValueError('Unknown expression, define a new case:\n'
                             '        elif expr == "{0}":\n'
                             '            return {0}'.format(expr))
    except KeyError as e:
        raise ValueError("Asking for evaluation of symbol '{}' but this has "
                         "not been defined or not yet computed".format(
                             e.message))


def check_spglib_version():
    """
    Check the SPGLIB version and raise a ValueError if the version is
    older than 1.9.4.

    Also raises an warning if the user has a version of SPGLIB that is
    older than 1.13, because before then there were some bugs (e.g. 
    wrong treatment of oI, see e.g. issue )

    Return the spglib module.
    """
    try:
        import spglib
    except ImportError:
        raise ValueError("spglib >= 1.9.4 is required for the creation "
                         "of the k-paths, but it could not be imported")

    try:
        version = spglib.__version__
    except NameError:
        version = "1.8.0"  # or older, version was introduced only recently

    try:
        version_pieces = [int(_) for _ in version.split('.')]
        if len(version_pieces) < 3:
            raise ValueError
    except ValueError:
        raise ValueError("Unable to parse version number")

    if tuple(version_pieces[:2]) < (1, 9):
        raise ValueError("Invalid spglib version, need >= 1.9.4")

    if version_pieces[:2] == (1, 9) and version_pieces[2] < 4:
        raise ValueError("Invalid spglib version, need >= 1.9.4")

    if tuple(version_pieces[:2]) < (1, 13):
        import warnings
        warnings.warn(
            'You have a version of SPGLIB older than 1.13, '
            'please consider upgrading to 1.13 or later since some bugs '
            'have been fixed', RuntimeWarning)

    return spglib


def get_cell_params(cell):
    r"""
    Return (a,b,c,cosalpha,cosbeta,cosgamma) given a :math:`3\times 3` cell
   
    .. note:: Rows are vectors: ``v1 = cell[0]``, ``v2 = cell[1]``, ``v3 = cell[3]``
    """
    import numpy
    from math import sqrt

    v1, v2, v3 = numpy.array(cell)
    a = sqrt(sum(v1**2))
    b = sqrt(sum(v2**2))
    c = sqrt(sum(v3**2))
    cosalpha = numpy.dot(v2, v3) / b / c
    cosbeta = numpy.dot(v1, v3) / a / c
    cosgamma = numpy.dot(v1, v2) / a / b

    return (a, b, c, cosalpha, cosbeta, cosgamma)


def get_reciprocal_cell_rows(real_space_cell):
    r"""
    Given the cell in real space (3x3 matrix, vectors as rows, 
    return the reciprocal-space cell where again the G vectors are 
    rows, i.e. satisfying 
    ``dot(real_space_cell, reciprocal_space_cell.T)`` = :math:`2 \pi I`,
    where :math:`I` is the :math:`3\times 3` identity matrix.

    :return: the :math:`3\times 3` list of reciprocal lattice vectors where each row is 
        one vector.
    """
    reciprocal_space_columns = 2. * numpy.pi * \
        numpy.linalg.inv(real_space_cell)
    return (reciprocal_space_columns.T).tolist()


def get_real_cell_from_reciprocal_rows(reciprocal_space_rows):
    r"""
    Given the cell in reciprocal space (3x3 matrix, G vectors as rows, 
    return the real-space cell where again the R vectors are 
    rows, i.e. satisfying 
    ``dot(real_space_cell, reciprocal_space_cell.T)`` = :math:`2 \pi I`,
    where :math:`I` is the :math:`3\times 3` identity matrix.

    .. note::  This is actually the same as :py:func:`get_reciprocal_cell_rows`.

    :return: the :math:`3\times 3` list of real lattice vectors where each row is 
        one vector.
    """
    real_space_columns = 2. * numpy.pi * \
        numpy.linalg.inv(reciprocal_space_rows)
    return (real_space_columns.T).tolist()


def get_path_data(ext_bravais):
    """
    Given an extended Bravais symbol among those defined in the HPKOT paper
    (only first three characters, like cF1), return the points and the 
    suggested path.

    :param ext_bravais: a string among the allowed etended Bravais lattices 
        defined in HPKOT.
    :return: a tuple ``(kparam_def, points_def, path)`` where the
        first element is the list with the definition of the
        k-point parameters, the second is the dictionary with the 
        definition of the k-points, and the third is the list
        with the suggested paths.

    .. note:: ``kparam_def`` has to be a list and not a dictionary
        because the order matters (later k-parameters can be defined
        in terms of previous ones)
    """
    import os

    # Get the data from the band_data folder
    this_folder = os.path.split(os.path.abspath(__file__))[0]
    folder = os.path.join(this_folder, "band_path_data", ext_bravais)
    path_file = os.path.join(folder, "path.txt")
    points_file = os.path.join(folder, "points.txt")
    kparam_file = os.path.join(folder, "k_vector_parameters.txt")
    with open(kparam_file) as f:
        kparam_raw = [_.split() for _ in f.readlines() if _.strip()]
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
    # order must be preserved here
    kparam_def = [(_[0], _[1].strip()) for _ in kparam_raw]
    points_def = {}
    for label, kPx, kPy, kPz in points_raw:
        if label in points_def:
            raise ValueError("Internal error! Point {} defined multiple times "
                             "for Bravais lattice {}".format(
                                 label, ext_bravais))
        points_def[label] = (kPx, kPy, kPz)
    path = [(_[0], _[1]) for _ in path_raw]

    # check path is valid
    for p1, p2 in path:
        if p1 not in points_def:
            raise ValueError(
                "Point {} found in path (for {}) but undefined!".format(
                    p1, ext_bravais))
        if p2 not in points_def:
            raise ValueError(
                "Point {} found in path (for {}) but undefined!".format(
                    p2, ext_bravais))

    return (kparam_def, points_def, path)
