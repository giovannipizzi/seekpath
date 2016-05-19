def get_crystal_family(number):
    """
    Given a spacegroup number, returns a string to identify its
    crystal family (triclinic, monoclinic, ...).

    :param number: the spacegroup number, from 1 to 230
    """
    if not isinstance(number, (int,long)):
        raise TypeError("number should be integer")
    if number < 1:
        raise ValueError("number should be >= 1")
    if number <= 2:
        return "a" # triclinic
    elif number <= 15:
        return "m" # monoclinic
    elif number <= 74:
        return "o" # orthorhombic
    elif number <= 142:
        return "t" # tetragonal
    elif number <= 194:
        return "h" # trigonal + hexagonal
    elif number <= 230:
        return "c" # cubic
    else:
        raise ValueError("number should be <= 230")

def pointgroup_has_inversion(number):
    """
    Return True if the pointgroup with given number has inversion, 
    False otherwise.

    :param number: The integer number of the pointgroup, from 1 to 32.
    """
    if number in [2,5,8,11,15,17,20,23,27,29,32]:
        return True
    elif number in [1,3,4,6,7,9,10,12,13,14,16,18,19,21,22,24,25,26,28,30,31]:
        return False
    else:
        raise ValueError("number should be between 1 and 32")


def pgnum_from_pgint(pgint):
    """
    Return the number of the pointgroup (from 1 to 32) from the
    international pointgroup name.
    """
    table = {u'C1': 1,
             u'C2': 3,
             u'C2h': 5,
             u'C2v': 7,
             u'C3': 16,
             u'C3h': 22,
             u'C3i': 17,
             u'C3v': 19,
             u'C4': 9,
             u'C4h': 11,
             u'C4v': 13,
             u'C6': 21,
             u'C6h': 23,
             u'C6v': 25,
             u'Ci': 2,
             u'Cs': 4,
             u'D2': 6,
             u'D2d': 14,
             u'D2h': 8,
             u'D3': 18,
             u'D3d': 20,
             u'D3h': 26,
             u'D4': 12,
             u'D4h': 15,
             u'D6': 24,
             u'D6h': 27,
             u'O': 30,
             u'Oh': 32,
             u'S4': 10,
             u'T': 28,
             u'Td': 31,
             u'Th': 29}

    return table[pgint]

def get_spgroup_data():
    """
    Return a dictionary that has the spacegroup number as key, and a tuple 
    as value, with (crystal family letter, centering, has_inversion).

    It loads if from a table in the source code for efficiency.
    """
    from .spg_db import spgroup_data
    return spgroup_data

def get_spgroup_data_realtime():
    """
    Return a dictionary that has the spacegroup number as key, and a tuple 
    as value, with (crystal family letter, centering, has_inversion),
    got in real time using spglib methods.
    """
    import json
    import spglib

    info = {}
    for hall_n in range(1,531):
        data = spglib.get_spacegroup_type(hall_n)
        number = data['number']
        int_short = data['international_short']
        pg_int = data['pointgroup_international']
        
        if number not in info:
            info[int(number)] = (get_crystal_family(number), # get cyrstal family
                            int_short[0], #centering from the first letter of the first spacegroup that I encounter
                            pointgroup_has_inversion(pgnum_from_pgint(pg_int)), # pointgroup has inversion
                            )
    return info
