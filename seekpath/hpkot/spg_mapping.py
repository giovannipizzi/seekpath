"""Tools to map a spagegroup to the crystal family or similar requirements."""


def get_crystal_family(number):
    """
    Given a spacegroup number, returns a string to identify its
    crystal family (triclinic, monoclinic, ...).

    :param number: the spacegroup number, from 1 to 230
    """
    if not isinstance(number, int):
        raise TypeError('number should be integer')
    if number < 1:
        raise ValueError('number should be >= 1')
    if number <= 2:
        return 'a'  # triclinic
    if number <= 15:
        return 'm'  # monoclinic
    if number <= 74:
        return 'o'  # orthorhombic
    if number <= 142:
        return 't'  # tetragonal
    if number <= 194:
        return 'h'  # trigonal + hexagonal
    if number <= 230:
        return 'c'  # cubic
    raise ValueError('number should be <= 230')


def pointgroup_has_inversion(number):
    """
    Return True if the pointgroup with given number has inversion,
    False otherwise.

    :param number: The integer number of the pointgroup, from 1 to 32.
    """
    if number in [2, 5, 8, 11, 15, 17, 20, 23, 27, 29, 32]:
        return True
    if number in [
        1,
        3,
        4,
        6,
        7,
        9,
        10,
        12,
        13,
        14,
        16,
        18,
        19,
        21,
        22,
        24,
        25,
        26,
        28,
        30,
        31,
    ]:
        return False
    raise ValueError('number should be between 1 and 32')


def pgnum_from_pgint(pgint):
    """
    Return the number of the pointgroup (from 1 to 32) from the
    international pointgroup name.
    """
    table = {
        'C1': 1,
        'C2': 3,
        'C2h': 5,
        'C2v': 7,
        'C3': 16,
        'C3h': 22,
        'C3i': 17,
        'C3v': 19,
        'C4': 9,
        'C4h': 11,
        'C4v': 13,
        'C6': 21,
        'C6h': 23,
        'C6v': 25,
        'Ci': 2,
        'Cs': 4,
        'D2': 6,
        'D2d': 14,
        'D2h': 8,
        'D3': 18,
        'D3d': 20,
        'D3h': 26,
        'D4': 12,
        'D4h': 15,
        'D6': 24,
        'D6h': 27,
        'O': 30,
        'Oh': 32,
        'S4': 10,
        'T': 28,
        'Td': 31,
        'Th': 29,
    }

    return table[pgint]


def get_spgroup_data():
    """
    Return a dictionary that has the spacegroup number as key, and a tuple
    as value, with content::

      (crystal family letter, centering, has_inversion).

    It loads if from a table in the source code for efficiency.
    """
    from .spg_db import spgroup_data

    return spgroup_data


def get_spgroup_data_realtime():
    """
    Return a dictionary that has the spacegroup number as key, and a tuple
    as value, with content::

       (crystal family letter, centering, has_inversion),

    got in real time using spglib methods.
    """
    import spglib
    from .tools import get_dot_access_dataset

    info = {}
    for hall_n in range(1, 531):
        data = get_dot_access_dataset(spglib.get_spacegroup_type(hall_n))
        number = data.number
        int_short = data.international_short
        pg_int = data.pointgroup_international

        if number not in info:
            info[int(number)] = (
                get_crystal_family(number),  # get cyrstal family
                # centering from the first letter of the first
                # spacegroup that I encounter
                int_short[0],
                pointgroup_has_inversion(
                    pgnum_from_pgint(pg_int)
                ),  # pointgroup has inversion
            )
    return info


def get_P_matrix(bravais_lattice):
    r"""
    Return a tuple of length 2 with the P matrix and its inverse::

      (P, invP)

    with :math:`invP = P^{-1}`.

    These :math:`P` matrices are obtained from Table 3 of the HPKOT
    paper.

    The P matrix is a :math:`3\times 3` matrix is the matrix that converts
    the lattice vectors from crystallographic conventional
    :math:`(a,b,c)` to crystallographic primitive :math:`(a_P, b_P, c_P)`
    as follows: :math:`(a_P, b_P, c_P) = (a,b,c) P`

    The change of (real space) coordinate triples follows instead:
    :math:`(x_P, y_P, z_P)^T = (P^{-1}) (x,y,z)^T`

    .. note:: the :math:`invP = P^{-1}` matrix is always integer (with values
        only :math:`-1, 0, 1`) while :math:`P` is rational (non-integer values can be
        :math:`\pm \frac 1 2` and :math:`\pm \frac 1 3`).
    """
    import numpy as np

    if bravais_lattice in ['cP', 'tP', 'hP', 'oP', 'mP']:
        P = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        invP = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    elif bravais_lattice in ['cF', 'oF']:
        P = 1.0 / 2.0 * np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
        invP = np.array([[-1, 1, 1], [1, -1, 1], [1, 1, -1]])
    elif bravais_lattice in ['cI', 'tI', 'oI']:
        P = 1.0 / 2.0 * np.array([[-1, 1, 1], [1, -1, 1], [1, 1, -1]])
        invP = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
    elif bravais_lattice == 'hR':
        P = 1.0 / 3.0 * np.array([[2, -1, -1], [1, 1, -2], [1, 1, 1]])
        invP = np.array([[1, 0, 1], [-1, 1, 1], [0, -1, 1]])
    elif bravais_lattice == 'oC':
        P = 1.0 / 2.0 * np.array([[1, 1, 0], [-1, 1, 0], [0, 0, 2]])
        invP = np.array([[1, -1, 0], [1, 1, 0], [0, 0, 1]])
    elif bravais_lattice == 'oA':
        P = 1.0 / 2.0 * np.array([[0, 0, 2], [1, 1, 0], [-1, 1, 0]])
        invP = np.array([[0, 1, -1], [0, 1, 1], [1, 0, 0]])
    elif bravais_lattice == 'mC':
        P = 1.0 / 2.0 * np.array([[1, -1, 0], [1, 1, 0], [0, 0, 2]])
        invP = np.array([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])
    elif bravais_lattice == 'aP':
        # For aP, I should have already obtained the primitive cell
        P = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        invP = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    else:
        raise ValueError(f'Invalid bravais_lattice {bravais_lattice}')

    return P, invP


def get_primitive(structure, bravais_lattice, wrap_to_zero_one=False):
    """
    Return the primitive cell from a conventional crystallographic cell.

    :note: the input structure MUST be already standardized by spglib!

    :param structure: should be a tuple of the form
      (lattice, positions, types) and it MUST be already a conventional
      crystallographic cell (i.e. as returned by spglib with the ``std_``
      prefix).

    :param bravais_lattice: a string with the information of the
      Bravais lattice of the input structure.

    :param wrap_to_zero_one: if True, wrap the scaled coordinates to the
       :math:`[0,1[` interval. Otherwise, the scaled coordinates will not be
       changed and can be outside of the :math:`[0,1[` range; the advantage is that
       the Cartesian coordinates of each atom returned in the primitive
       cell will match with one of the atoms in the input structure if this
       variable is False.

    :return: a tuple of length three: the first element is the primitive
        structure, also in the format (lattice, positions, types); the second
        is a tuple with the ``(P, invP)`` matrices as returned by :py:func:`get_P_matrix`; the
        third is an array with the mapping from the atoms in the conventional
        cell to the atoms in the primitive cell (e.g. if the conventional cell
        has four atoms and twice the volume than the primitive, and the first
        and third atoms in the conventional map to the first of the primitive,
        while the second and the fourth map to the second of the primitive,
        this array will be :math:`[0,1,0,1]`).
    """
    import numpy as np
    from collections import Counter

    threshold = 1.0e-6  # Threshold for creation of primitive cell

    lattice, positions, types = structure
    P, invP = get_P_matrix(bravais_lattice)

    volume_ratio = int(round(np.linalg.det(invP)))

    # (a_P, b_P, c_P) = (a,b,c) P
    # a is the first ROW of lattice => I have to transpose lattice
    prim_lattice = np.dot(np.array(np.array(lattice).T), P).T
    # (x_P, y_P, z_P)^T = (P^-1) (x,y,z)^T
    prim_positions = np.dot(invP, np.array(positions).T).T

    # Now I need to remove duplicates
    # I get if the x coord is the same, modulo one
    # I compare all with all
    # (I will get a NxN matrix, where N = number of atoms)
    # I shift by 1/2, do %1 and then shift back so that I get values between
    # -0.5 and 0.5 rather than between 0 and 1, which would be problematic
    # to find values close to zero
    x_match = (
        np.abs(
            ((prim_positions[:, 0] - prim_positions[:, 0][:, None] + 0.5) % 1.0) - 0.5
        )
        < threshold
    )
    y_match = (
        np.abs(
            ((prim_positions[:, 1] - prim_positions[:, 1][:, None] + 0.5) % 1.0) - 0.5
        )
        < threshold
    )
    z_match = (
        np.abs(
            ((prim_positions[:, 2] - prim_positions[:, 2][:, None] + 0.5) % 1.0) - 0.5
        )
        < threshold
    )
    # To be the same, they should all match
    all_match = np.logical_and(x_match, np.logical_and(y_match, z_match))

    # list of ids, each row identifies a group of equivalent atoms
    # I convert to tuple so they can become keys of a dict for counting
    group_of_equivalent_atoms = [
        tuple(np.arange(all_match.shape[0])[row]) for row in all_match
    ]
    group_count = Counter(group_of_equivalent_atoms)
    wrong_count = [group for group, cnt in group_count.items() if cnt != volume_ratio]
    if wrong_count:
        raise ValueError(
            'Problem creating primitive cell, I found the '
            f'following group of atoms with len != {volume_ratio}:'
            f' {", ".join(str(_) for _ in wrong_count)}'
        )
    # These are the groups of equivalent atoms; values are the positions in
    # the list from 0 to N-1
    groups = sorted(group_count.keys())
    # I check that the type is always the same
    unique_types = [set(np.array(types)[np.array(group)]) for group in groups]
    problematic_groups_idx = list(
        group_idx
        for group_idx, type_set in enumerate(unique_types)
        if len(type_set) != 1
    )
    if problematic_groups_idx:
        problematic_groups_str = ', '.join(
            [
                str(group)
                for group_idx, group in enumerate(groups)
                if group_idx in problematic_groups_idx
            ]
        )
        raise ValueError(
            'The following ids of atoms go on top of each other, '
            f'but they are of different type! {problematic_groups_str}'
        )
    # All good, just return the first (no wrapping to [0..1[ yet)
    chosen_idx = np.array([group[0] for group in groups])

    # Create the list of mapped atoms
    conv_prim_atoms_mapping = -1 * np.ones(len(positions), dtype=int)
    for prim_idx, group in enumerate(groups):
        for at_idx in group:
            conv_prim_atoms_mapping[at_idx] = prim_idx
    if -1 in conv_prim_atoms_mapping:
        raise ValueError(
            f'Unable to recreate correctly the atom mapping! {conv_prim_atoms_mapping}'
        )

    prim_positions = prim_positions[chosen_idx]
    prim_types = np.array(types)[chosen_idx]

    if wrap_to_zero_one:
        prim_positions = prim_positions % 1.0

    prim_structure = (prim_lattice, prim_positions, prim_types)

    return (prim_structure, (P, invP), conv_prim_atoms_mapping)
