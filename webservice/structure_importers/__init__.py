import ase.io
from ase.data import atomic_numbers

def get_atomic_numbers(symbols):
    """
    Given a list of symbols, return the corresponding atomic numbers.

    :raise ValueError: if the symbol is not recognized
    """
    retlist = []
    for s in symbols:
        try:
            retlist.append(atomic_numbers[s])
        except KeyError:
            raise ValueError("Unknown symbol '{}'".format(s))
    return retlist

def tuple_from_ase(asestructure):
    """
    Given a ASE structure, return a structure tuple as expected from seekpath

    :param asestructure: a ASE Atoms object
    
    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    atomic_numbers = get_atomic_numbers(
        asestructure.get_chemical_symbols())
    structure_tuple = (
        asestructure.cell.tolist(),
        asestructure.get_scaled_positions().tolist(),
        atomic_numbers)
    return structure_tuple

def get_structure_tuple(fileobject, fileformat):        
    """
    Given a file-like object (using StringIO or open()), and a string
    identifying the file format, return a structure tuple as accepted
    by seekpath.

    :param fileobject: a file-like object containing the file content
    :param fileformat: a string with the format to use to parse the data

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    if fileformat == 'vasp':
        import ase.io.vasp
        asestructure = ase.io.vasp.read_vasp(fileobject)
        return tuple_from_ase(asestructure)
    elif fileformat == 'xsf':
        import ase.io.xsf
        asestructure = ase.io.xsf.read_xsf(fileobject)
        return tuple_from_ase(asestructure)
    elif fileformat == 'qe-inp':
        from .qeinp import read_qeinp
        structure_tuple = read_qeinp(fileobject)
        return structure_tuple
    else:
        raise UnknownFormatError(fileformat)

    # I should never be here, I raise anyway a UnknownFormatError
    raise UnknownFormatError(fileformat)    

