"""Various utilities."""

import numpy
import numpy.linalg
from math import sqrt

import sys
from packaging.version import Version

# Use importlib.metadata for version retrieval based on Python version
if sys.version_info < (3, 8):
    from importlib_metadata import version  # For Python < 3.8
else:
    from importlib.metadata import version


def eval_expr_simple(expr, kparam):  # pylint=disable: too-many-return-statements
    """
    To evaluate expressions tha only require kparams and not a, b, c, ...
    """
    if expr == '0':
        return 0.0
    if expr == '1/2':
        return 1.0 / 2.0
    if expr == '1':
        return 1.0
    if expr == '-1/2':
        return -1.0 / 2.0
    if expr == '1/4':
        return 1.0 / 4.0
    if expr == '3/8':
        return 3.0 / 8.0
    if expr == '3/4':
        return 3.0 / 4.0
    if expr == '5/8':
        return 5.0 / 8.0
    if expr == '1/3':
        return 1.0 / 3.0
    try:
        return kparam[expr]
    except KeyError as exc:
        raise ValueError(
            f"Asking for evaluation of symbol '{str(exc)}' in "
            'eval_expr_simple but this has not been defined or not '
            'yet computed'
        ) from exc


def extend_kparam(kparam):
    """
    Extend the list of kparam with also expressions like :math:`1-x`, ...

    :param kparam: a dictionary where the key is the expression as a string and
       the value is the numerical value
    :return: a similar dictionary, extended with simple expressions
    """
    kparam_extended = {}
    for key, val in kparam.items():
        kparam_extended[key] = val
        kparam_extended[f'-{key}'] = -val
        kparam_extended[f'1-{key}'] = 1.0 - val
        kparam_extended[f'-1+{key}'] = -1.0 + val
        kparam_extended[f'1/2-{key}'] = 1.0 / 2.0 - val
        kparam_extended[f'1/2+{key}'] = 1.0 / 2.0 + val

    return kparam_extended


def eval_expr(  # pylint: disable=too-many-return-statements,unused-argument
    expr, a, b, c, cosalpha, cosbeta, cosgamma, kparam
):
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

    # sinalpha = sqrt(1.0 - cosalpha ** 2)
    sinbeta = sqrt(1.0 - cosbeta**2)
    # singamma = sqrt(1.0 - cosgamma ** 2)

    try:
        if expr == '(a*a/b/b+(1+a/c*cosbeta)/sinbeta/sinbeta)/4':
            return (a * a / b / b + (1.0 + a / c * cosbeta) / sinbeta / sinbeta) / 4.0
        if expr == '1-Z*b*b/a/a':
            Z = kparam['Z']
            return 1.0 - Z * b * b / a / a
        if expr == '1/2-2*Z*c*cosbeta/a':
            Z = kparam['Z']
            return 1.0 / 2.0 - 2.0 * Z * c * cosbeta / a
        if expr == 'E/2+a*a/4/b/b+a*c*cosbeta/2/b/b':
            E = kparam['E']
            return E / 2.0 + a * a / 4.0 / b / b + a * c * cosbeta / 2.0 / b / b
        if expr == '2*F-Z':
            F = kparam['F']
            Z = kparam['Z']
            return 2.0 * F - Z
        if expr == 'c/2/a/cosbeta*(1-4*U+a*a*sinbeta*sinbeta/b/b)':
            U = kparam['U']
            return (
                c
                / 2.0
                / a
                / cosbeta
                * (1.0 - 4.0 * U + a * a * sinbeta * sinbeta / b / b)
            )
        if expr == '-1/4+W/2-Z*c*cosbeta/a':
            W = kparam['W']
            Z = kparam['Z']
            return -1.0 / 4.0 + W / 2.0 - Z * c * cosbeta / a
        if expr == '(2+a/c*cosbeta)/4/sinbeta/sinbeta':
            return (2.0 + a / c * cosbeta) / 4.0 / sinbeta / sinbeta
        if expr == '3/4-b*b/4/a/a/sinbeta/sinbeta':
            return 3.0 / 4.0 - b * b / 4.0 / a / a / sinbeta / sinbeta
        if expr == 'S-(3/4-S)*a*cosbeta/c':
            S = kparam['S']
            return S - (3.0 / 4.0 - S) * a * cosbeta / c
        if expr == '(1+a*a/b/b)/4':
            return (1.0 + a * a / b / b) / 4.0
        if expr == '-a*c*cosbeta/2/b/b':
            return -a * c * cosbeta / 2.0 / b / b
        if expr == '1+Z-2*M':
            Z = kparam['Z']
            M = kparam['M']
            return 1.0 + Z - 2.0 * M
        if expr == 'X-2*D':
            X = kparam['X']
            D = kparam['D']
            return X - 2 * D
        if expr == '(1+a/c*cosbeta)/2/sinbeta/sinbeta':
            return (1.0 + a / c * cosbeta) / 2.0 / sinbeta / sinbeta
        if expr == '1/2+Y*c*cosbeta/a':
            Y = kparam['Y']
            return 1.0 / 2.0 + Y * c * cosbeta / a
        if expr == 'a*a/4/c/c':
            return a * a / 4.0 / c / c
        if expr == '5/6-2*D':
            D = kparam['D']
            return 5.0 / 6.0 - 2.0 * D
        if expr == '1/3+D':
            D = kparam['D']
            return 1.0 / 3.0 + D
        if expr == '1/6-c*c/9/a/a':
            return 1.0 / 6.0 - c * c / 9.0 / a / a
        if expr == '1/2-2*Z':
            Z = kparam['Z']
            return 1.0 / 2.0 - 2.0 * Z
        if expr == '1/2+Z':
            Z = kparam['Z']
            return 1.0 / 2.0 + Z
        if expr == '(1+b*b/c/c)/4':
            return (1.0 + b * b / c / c) / 4.0
        if expr == '(1+c*c/b/b)/4':
            return (1.0 + c * c / b / b) / 4.0
        if expr == '(1+b*b/a/a)/4':
            return (1.0 + b * b / a / a) / 4.0
        if expr == '(1+a*a/b/b-a*a/c/c)/4':
            return (1.0 + a * a / b / b - a * a / c / c) / 4.0
        if expr == '(1+a*a/b/b+a*a/c/c)/4':
            return (1.0 + a * a / b / b + a * a / c / c) / 4.0
        if expr == '(1+c*c/a/a-c*c/b/b)/4':
            return (1.0 + c * c / a / a - c * c / b / b) / 4.0
        if expr == '(1+c*c/a/a+c*c/b/b)/4':
            return (1.0 + c * c / a / a + c * c / b / b) / 4.0
        if expr == '(1+b*b/a/a-b*b/c/c)/4':
            return (1.0 + b * b / a / a - b * b / c / c) / 4.0
        if expr == '(1+c*c/b/b-c*c/a/a)/4':
            return (1.0 + c * c / b / b - c * c / a / a) / 4.0
        if expr == '(1+a*a/c/c)/4':
            return (1.0 + a * a / c / c) / 4.0
        if expr == '(b*b-a*a)/4/c/c':
            return (b * b - a * a) / 4.0 / c / c
        if expr == '(a*a+b*b)/4/c/c':
            return (a * a + b * b) / 4.0 / c / c
        if expr == '(1+c*c/a/a)/4':
            return (1.0 + c * c / a / a) / 4.0
        if expr == '(c*c-b*b)/4/a/a':
            return (c * c - b * b) / 4.0 / a / a
        if expr == '(b*b+c*c)/4/a/a':
            return (b * b + c * c) / 4.0 / a / a
        if expr == '(a*a-c*c)/4/b/b':
            return (a * a - c * c) / 4.0 / b / b
        if expr == '(c*c+a*a)/4/b/b':
            return (c * c + a * a) / 4.0 / b / b
        if expr == 'a*a/2/c/c':
            return a * a / 2.0 / c / c
        raise ValueError(
            'Unknown expression, define a new case:\n'
            f'        elif expr == "{expr}":\n'
            f'            return {expr}'
        )
    except KeyError as exc:
        raise ValueError(
            f"Asking for evaluation of symbol '{str(exc)}' but this has "
            'not been defined or not yet computed'
        ) from exc


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
    except ImportError as exc:
        raise ValueError(
            'spglib >= 1.9.4 is required for the creation '
            'of the k-paths, but it could not be imported'
        ) from exc

    spg_version = Version(version('spglib'))

    min_version = Version('1.9.4')
    warning_version = Version('1.13')

    if spg_version < min_version:
        raise ValueError('Invalid spglib version, need >= 1.9.4')

    if spg_version < warning_version:
        import warnings

        warnings.warn(
            'You have a version of SPGLIB older than 1.13, '
            'please consider upgrading to 1.13 or later since some bugs '
            'have been fixed',
            RuntimeWarning,
        )

    return spglib


def get_dot_access_dataset(dataset):
    """Return dataset with dot access.

    From spglib 2.5, dataset is returned as dataclass.
    To emulate it for older versions, this function is used.

    """
    spg_version = Version(version('spglib'))

    if spg_version < Version('2.5.0'):
        from types import SimpleNamespace

        return SimpleNamespace(**dataset)

    return dataset


def get_cell_params(cell):
    r"""
    Return (a,b,c,cosalpha,cosbeta,cosgamma) given a :math:`3\times 3` cell

    .. note:: Rows are vectors: ``v1 = cell[0]``, ``v2 = cell[1]``, ``v3 = cell[3]``
    """
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
    reciprocal_space_columns = 2.0 * numpy.pi * numpy.linalg.inv(real_space_cell)
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
    real_space_columns = 2.0 * numpy.pi * numpy.linalg.inv(reciprocal_space_rows)
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
    folder = os.path.join(this_folder, 'band_path_data', ext_bravais)
    path_file = os.path.join(folder, 'path.txt')
    points_file = os.path.join(folder, 'points.txt')
    kparam_file = os.path.join(folder, 'k_vector_parameters.txt')
    with open(kparam_file, encoding='utf-8') as f:
        kparam_raw = [_.split() for _ in f.readlines() if _.strip()]
    with open(points_file, encoding='utf-8') as f:
        points_raw = [_.split() for _ in f.readlines()]
    with open(path_file, encoding='utf-8') as f:
        path_raw = [_.split() for _ in f.readlines()]

    # check
    if any(len(_) != 2 for _ in kparam_raw):
        raise ValueError(f'Invalid line length in {kparam_file}')
    if any(len(_) != 2 for _ in path_raw):
        raise ValueError(f'Invalid line length in {path_file}')
    if any(len(_) != 4 for _ in points_raw):
        raise ValueError(f'Invalid line length in {points_file}')
    # order must be preserved here
    kparam_def = [(_[0], _[1].strip()) for _ in kparam_raw]
    points_def = {}
    for label, kPx, kPy, kPz in points_raw:
        if label in points_def:
            raise ValueError(
                f'Internal error! Point {label} defined multiple times '
                f'for Bravais lattice {ext_bravais}'
            )
        points_def[label] = (kPx, kPy, kPz)
    path = [(_[0], _[1]) for _ in path_raw]

    # check path is valid
    for p1, p2 in path:
        if p1 not in points_def:
            raise ValueError(
                f'Point {p1} found in path (for {ext_bravais}) but undefined!'
            )
        if p2 not in points_def:
            raise ValueError(
                f'Point {p2} found in path (for {ext_bravais}) but undefined!'
            )

    return (kparam_def, points_def, path)
