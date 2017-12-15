from builtins import zip
from seekpath import (
    get_explicit_k_path as _raw_explicit_path,
    get_path as _raw_get_path)


def _aiida_to_tuple(aiida_structure):
    """
    Convert an AiiDA structure to a tuple of the format
    (cell, scaled_positions, element_numbers).

    :param aiida_structure: the AiiDA structure
    :return: (structure_tuple, kind_info, kinds) where structure_tuple
       is a tuple of format (cell, scaled_positions, element_numbers);
       kind_info is a dictionary mapping the kind_names to
       the numbers used in element_numbers. When possible, it uses
       the Z number of the element, otherwise it uses numbers > 1000;
       kinds is a list of the kinds of the structure.
    """
    import numpy as np
    from aiida.common.constants import elements

    def get_new_number(the_list, start_from):
        """
        Get the first integer >= start_from not yet in the list
        """
        retval = start_from
        comp_list = sorted(_ for _ in the_list if _ >= start_from)

        current_pos = 0
        found = False
        while not found:
            if len(comp_list) <= current_pos:
                return retval
            if retval == comp_list[current_pos]:
                current_pos += 1
                retval += 1
            else:
                found = True
                return retval

    Z = {v['symbol']: k for k, v in elements.items()}

    cell = np.array(aiida_structure.cell)
    abs_pos = np.array([_.position for _ in aiida_structure.sites])
    rel_pos = np.dot(abs_pos, np.linalg.inv(cell))
    kinds = {k.name: k for k in aiida_structure.kinds}

    kind_numbers = {}
    for kind in aiida_structure.kinds:
        if len(kind.symbols) == 1:
            realnumber = Z[kind.symbols[0]]
            if realnumber in list(kind_numbers.values()):
                number = get_new_number(
                    list(kind_numbers.values()), start_from=realnumber * 1000)
            else:
                number = realnumber
            kind_numbers[kind.name] = number
        else:
            number = get_new_number(list(kind_numbers.values()), start_from=200000)
            kind_numbers[kind.name] = number

    numbers = [kind_numbers[s.kind_name] for s in aiida_structure.sites]

    return ((cell, rel_pos, numbers), kind_numbers, list(aiida_structure.kinds))


def _tuple_to_aiida(structure_tuple, kind_info=None, kinds=None):
    """
    Convert an tuple of the format
    (cell, scaled_positions, element_numbers) to an AiiDA structure.

    Unless the element_numbers are identical to the Z number of the atoms,
    you should pass both kind_info and kinds, with the same format as returned
    by get_tuple_from_aiida_structure.

    :param structure_tuple: the structure in format (structure_tuple, kind_info)
    :param kind_info: a dictionary mapping the kind_names to
       the numbers used in element_numbers. If not provided, assumes {element_name: element_Z}
    :param kinds: a list of the kinds of the structure.
    """
    from aiida.common.constants import elements
    from aiida.orm.data.structure import Kind, Site, StructureData
    import numpy as np
    import copy

    if kind_info is None and kinds is not None:
        raise ValueError("If you pass kind_info, you should also pass kinds")
    if kinds is None and kind_info is not None:
        raise ValueError("If you pass kinds, you should also pass kind_info")

    Z = {v['symbol']: k for k, v in elements.items()}
    cell, rel_pos, numbers = structure_tuple
    if kind_info:
        _kind_info = copy.copy(kind_info)
        _kinds = copy.copy(kinds)
    else:
        try:
            # For each site
            symbols = [elements[num]['symbol'] for num in numbers]
        except KeyError as e:
            raise ValueError("You did not pass kind_info, but at least one number "
                             "is not a valid Z number: {}".format(e.message))

        _kind_info = {elements[num]['symbol']: num for num in set(numbers)}
        # Get the default kinds
        _kinds = [Kind(symbols=sym) for sym in set(symbols)]

    _kinds_dict = {k.name: k for k in _kinds}
    # Now I will use in any case _kinds and _kind_info
    if len(_kind_info.values()) != len(set(_kind_info.values())):
        raise ValueError(
            "There is at least a number repeated twice in kind_info!")
    # Invert the mapping
    mapping_num_kindname = {v: k for k, v in _kind_info.items()}
    # Create the actual mapping
    try:
        mapping_to_kinds = {num: _kinds_dict[kindname] for num, kindname
                            in mapping_num_kindname.items()}
    except KeyError as e:
        raise ValueError(
            "Unable to find '{}' in the kinds list".format(e.message))

    try:
        site_kinds = [mapping_to_kinds[num] for num in numbers]
    except KeyError as e:
        raise ValueError(
            "Unable to find kind in kind_info for number {}".format(e.message))

    out_structure = StructureData(cell=cell)
    for k in _kinds:
        out_structure.append_kind(k)
    abs_pos = np.dot(rel_pos, cell)
    if len(abs_pos) != len(site_kinds):
        raise ValueError("The length of the positions array is different from the "
                         "length of the element numbers")

    for kind, pos in zip(site_kinds, abs_pos):
        out_structure.append_site(Site(kind_name=kind.name, position=pos))

    return out_structure


def get_explicit_k_path(structure, parameters):
    """
    Return the kpoint path for band structure (in scaled and absolute 
    coordinates), given a crystal structure,
    using the paths proposed in the various publications (see description
    of the 'recipe' input parameter). The parameters are the same
    as get get_explicit_k_path in __init__, but here all structures are
    input and returned as AiiDA structures rather than tuples, and similarly
    k-points-related information as a AiiDA KpointsData class.

    :param structure: The AiiDA StructureData for which we want to obtain
        the suggested path. 

    :param parameters: A ParameterData. Its key-value pairs are passed as
        additional kwargs to the ``seekpath.get_explicit_k_path`` function.

    :return: A dictionary with four
        nodes:
        - ``seekpath_parameters``: a ParameterData, whose content is
          the same dictionary as returned by the ``seekpath.get_explicit_k_path`` function,
          except that:

          - ``conv_lattice``, ``conv_positions``, ``conv_types``
            are removed and replaced by the ``conv_structure`` output node

          - ``primitive_lattice``, ``primitive_positions``, ``primitive_types``
            are removed and replaced by the `primitive_structure` output node

          - ``reciprocal_primitive_lattice``, ``explicit_kpoints_abs``,  
            ``explicit_kpoints_rel`` and ``explicit_kpoints_labels`` are removed
            and replaced by the ``explicit_kpoints`` output node

        - ``primitive_structure``: A StructureData with the primitive structure

        - ``conv_structure``: A StructureData with the primitive structure

        - ``explicit_kpoints``: a KpointsData with the (explicit) kpoints
          (with labels set).
    """
    import copy
    from aiida.orm import DataFactory

    KpointsData = DataFactory('array.kpoints')
    ParameterData = DataFactory('parameter')

    struc_tuple, kind_info, kinds = _aiida_to_tuple(structure)

    retdict = {}
    rawdict = _raw_explicit_path(
        structure=struc_tuple,
        **parameters.get_dict())

    # Replace primitive structure with AiiDA StructureData
    primitive_lattice = rawdict.pop('primitive_lattice')
    primitive_positions = rawdict.pop('primitive_positions')
    primitive_types = rawdict.pop('primitive_types')
    primitive_tuple = (primitive_lattice, primitive_positions, primitive_types)
    primitive_structure = _tuple_to_aiida(primitive_tuple, kind_info, kinds)
    retdict['primitive_structure'] = primitive_structure

    # Replace conv structure with AiiDA StructureData
    conv_lattice = rawdict.pop('conv_lattice')
    conv_positions = rawdict.pop('conv_positions')
    conv_types = rawdict.pop('conv_types')
    conv_tuple = (conv_lattice, conv_positions, conv_types)
    conv_structure = _tuple_to_aiida(conv_tuple, kind_info, kinds)
    retdict['conv_structure'] = conv_structure

    # Remove reciprocal_primitive_lattice, recalculated by kpoints class
    rawdict.pop('reciprocal_primitive_lattice')
    kpoints_abs = rawdict.pop('explicit_kpoints_abs')
    kpoints_rel = rawdict.pop('explicit_kpoints_rel')
    kpoints_labels = rawdict.pop('explicit_kpoints_labels')
    # Expects something of the type [[0,'X'],[34,'L'],...]
    # So I generate it, skipping empty labels
    labels = [[idx, label] for idx, label in enumerate(kpoints_labels)
              if label]

    kpoints = KpointsData()
    kpoints.set_cell_from_structure(primitive_structure)
    kpoints.set_kpoints(
        kpoints_abs, cartesian=True, labels=labels)
    retdict['explicit_kpoints'] = kpoints
    retdict['seekpath_parameters'] = ParameterData(dict=rawdict)

    return retdict


def get_path(structure, parameters):
    """
    Return the kpoint path information for band structure given a 
    crystal structure, using the paths from the chosen recipe/reference.
    The parameters are the same
    as get get_path in __init__, but here all structures are
    input and returned as AiiDA structures rather than tuples.


    If you use this module, please cite the paper of the corresponding 
    recipe (see documentation of seekpath).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be an AiiDA StructureData object.

    :param parameters: A ParameterData. Its key-value pairs are passed as
        additional kwargs to the ``seekpath.get_path`` function.

    :return: A dictionary with three
        nodes:
        - ``seekpath_parameters``: a ParameterData, whose content is
          the same dictionary as returned by the ``seekpath.get_path`` function,
          except that:

          - ``conv_lattice``, ``conv_positions``, ``conv_types``
            are removed and replaced by the ``conv_structure`` output node

          - ``primitive_lattice``, ``primitive_positions``, ``primitive_types``
            are removed and replaced by the ``primitive_structure`` output node

        - ``primitive_structure``: A StructureData with the primitive structure

        - ``conv_structure``: A StructureData with the primitive structure
    """
    import copy
    from aiida.orm import DataFactory

    ParameterData = DataFactory('parameter')

    struc_tuple, kind_info, kinds = _aiida_to_tuple(structure)

    retdict = {}
    rawdict = _raw_get_path(
        structure=struc_tuple,
        **parameters.get_dict())

    # Replace conv structure with AiiDA StructureData
    conv_lattice = rawdict.pop('conv_lattice')
    conv_positions = rawdict.pop('conv_positions')
    conv_types = rawdict.pop('conv_types')
    conv_tuple = (conv_lattice, conv_positions, conv_types)
    conv_structure = _tuple_to_aiida(conv_tuple, kind_info, kinds)
    retdict['conv_structure'] = conv_structure

    # Replace primitive structure with AiiDA StructureData
    primitive_lattice = rawdict.pop('primitive_lattice')
    primitive_positions = rawdict.pop('primitive_positions')
    primitive_types = rawdict.pop('primitive_types')
    primitive_tuple = (primitive_lattice, primitive_positions, primitive_types)
    primitive_structure = _tuple_to_aiida(primitive_tuple, kind_info, kinds)
    retdict['primitive_structure'] = primitive_structure

    retdict['seekpath_parameters'] = ParameterData(dict=rawdict)

    return retdict
