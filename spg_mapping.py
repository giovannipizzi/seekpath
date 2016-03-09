def get_crystal_family(number):
    """
    Given a spacegroup number (from 1 to 230), returns a string to identify it is
    crystal family (triclinic, monoclinic, ...).
    """
    if not isinstance(number, int):
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
    Return True if the pointgroup with given number has inversion, False otherwise.
    """
    if number in [2,5,8,11,15,17,20,23,27,29,32]:
        return True
    if number in [1,3,4,6,7,9,10,12,13,14,16,18,19,21,22,24,25,26,28,30,31]:
        return False
    else:
        raise ValueError("number should be between 1 and 32")

def get_spgroup_data():
    """
    Return a dictionary that has the spacegroup number as key, and a tuple as value,
    with (crystal family letter, centering, has_inversion).
    """
    import json
    from spg_db import settings

    spgroups = {}
    for s in settings:
        number = int(s[0])
        if number == 0:
            continue
        data = {'name':   s[5].strip(),
                'pointgroup_number': s[8]
                }
        if number not in spgroups: # Just keep the first one (the name can change, e.g. P222_1 or P22_12 or P2_122) - Confimed by A. Togo
            spgroups[number] = data

    # contains (crystal_family, centering)
    info = {k: (get_crystal_family(k), v['name'][0], pointgroup_has_inversion(v['pointgroup_number'])) for k, v in spgroups.iteritems()}
    #info2 = {k: (v[0], v[1], "+" if v[2] else "-") for k, v in info.iteritems()}
    #print json.dumps({k: "{}{}{}".format(*v) for k, v in info2.iteritems()},indent=2)

    return info
 
