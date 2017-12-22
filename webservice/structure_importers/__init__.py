import ase.io
from ase.data import atomic_numbers
from seekpath.util import atoms_num_dict
import pymatgen
import qe_tools
import numpy as np


class UnknownFormatError(ValueError):
    pass


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
    atomic_numbers = get_atomic_numbers(asestructure.get_chemical_symbols())
    structure_tuple = (asestructure.cell.tolist(),
                       asestructure.get_scaled_positions().tolist(),
                       atomic_numbers)
    return structure_tuple


def tuple_from_pymatgen(pmgstructure):
    """
    Given a pymatgen structure, return a structure tuple as expected from seekpath

    :param pmgstructure: a pymatgen Structure object
    
    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    frac_coords = [site.frac_coords.tolist() for site in pmgstructure.sites]
    structure_tuple = (pmgstructure.lattice.matrix.tolist(), frac_coords,
                       pmgstructure.atomic_numbers)
    return structure_tuple


def get_structure_tuple(fileobject, fileformat, extra_data=None):
    """
    Given a file-like object (using StringIO or open()), and a string
    identifying the file format, return a structure tuple as accepted
    by seekpath.

    :param fileobject: a file-like object containing the file content
    :param fileformat: a string with the format to use to parse the data

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    ase_fileformats = {
        'vasp-ase': 'vasp',
        'xsf-ase': 'xsf',
        'castep-ase': 'castep-cell',
        'pdb-ase': 'proteindatabank',
        'xyz-ase': 'xyz',
        'cif-ase':
        'cif',  # currently broken in ASE: https://gitlab.com/ase/ase/issues/15
    }
    if fileformat in ase_fileformats.keys():
        asestructure = ase.io.read(
            fileobject, format=ase_fileformats[fileformat])

        if fileformat == 'xyz-ase':
            # XYZ does not contain cell information, add them back from the additional form data
            try:
                cell = list(
                    tuple(
                        float(extra_data['xyzCellVec' + v + a][0])
                        for a in 'xyz')
                    for v in 'ABC')
                # ^^^ avoid generator expressions by explicitly requesting tuple/list
            except (KeyError, ValueError):
                raise  # at some point we might want to convert the different conversion errors to a custom exception

            asestructure.set_cell(cell)

        return tuple_from_ase(asestructure)
    elif fileformat == "cif-pymatgen":
        from pymatgen.io.cif import CifParser
        # Only get the first structure, if more than one
        pmgstructure = CifParser(fileobject).get_structures()[0]
        return tuple_from_pymatgen(pmgstructure)
    elif fileformat == 'qeinp-qetools':
        pwfile = qe_tools.PwInputFile(fileobject)
        pwparsed = pwfile.get_structure_from_qeinput()

        cell = pwparsed['cell']
        rel_position = np.dot(pwparsed['positions'],
                              np.linalg.inv(cell)).tolist()
        numbers = [atoms_num_dict[sym] for sym in pwparsed['atom_names']]

        structure_tuple = (cell, rel_position, numbers)
        print(structure_tuple)
        return structure_tuple

    raise UnknownFormatError(fileformat)
