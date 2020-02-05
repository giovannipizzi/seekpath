from builtins import zip
from . import (get_explicit_k_path as _raw_explicit_path, get_path as
               _raw_get_path)

DEPRECATION_DOCS_URL = "http://seekpath.readthedocs.io/en/latest/maindoc.html#aiida-integration"


def _aiida_to_tuple(aiida_structure):
    """
    Convert an AiiDA structure to a tuple of the format
    (cell, scaled_positions, element_numbers).

    .. deprecated:: 1.8
      Use the methods in AiiDA instead.

    :param aiida_structure: the AiiDA structure
    :return: (structure_tuple, kind_info, kinds) where structure_tuple
       is a tuple of format (cell, scaled_positions, element_numbers);
       kind_info is a dictionary mapping the kind_names to
       the numbers used in element_numbers. When possible, it uses
       the Z number of the element, otherwise it uses numbers > 1000;
       kinds is a list of the kinds of the structure.
    """
    import warnings
    warnings.warn(
        'this method has been deprecated and moved to AiiDA, see {}'.format(
            DEPRECATION_DOCS_URL), DeprecationWarning)

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
                number = get_new_number(list(kind_numbers.values()),
                                        start_from=realnumber * 1000)
            else:
                number = realnumber
            kind_numbers[kind.name] = number
        else:
            number = get_new_number(list(kind_numbers.values()),
                                    start_from=200000)
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

    .. deprecated:: 1.8
      Use the methods in AiiDA instead.

    :param structure_tuple: the structure in format (structure_tuple, kind_info)
    :param kind_info: a dictionary mapping the kind_names to
       the numbers used in element_numbers. If not provided, assumes {element_name: element_Z}
    :param kinds: a list of the kinds of the structure.
    """
    import warnings
    warnings.warn(
        'this method has been deprecated and moved to AiiDA, see {}'.format(
            DEPRECATION_DOCS_URL), DeprecationWarning)

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
            raise ValueError(
                "You did not pass kind_info, but at least one number "
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
        mapping_to_kinds = {
            num: _kinds_dict[kindname]
            for num, kindname in mapping_num_kindname.items()
        }
    except KeyError as e:
        raise ValueError("Unable to find '{}' in the kinds list".format(
            e.message))

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
        raise ValueError(
            "The length of the positions array is different from the "
            "length of the element numbers")

    for kind, pos in zip(site_kinds, abs_pos):
        out_structure.append_site(Site(kind_name=kind.name, position=pos))

    return out_structure


def get_explicit_k_path(structure,
                        with_time_reversal=True,
                        reference_distance=0.025,
                        recipe='hpkot',
                        threshold=1.e-7):
    """
    Return the kpoint path for band structure (in scaled and absolute 
    coordinates), given a crystal structure,
    using the paths proposed in the various publications (see description
    of the 'recipe' input parameter). The parameters are the same
    as get get_explicit_k_path in __init__, but here all structures are
    input and returned as AiiDA structures rather than tuples, and similarly
    k-points-related information as a AiiDA KpointsData class.

    .. deprecated:: 1.8
      Use the methods in AiiDA instead.

    :param structure: The AiiDA StructureData for which we want to obtain
        the suggested path. 

    :param with_time_reversal: if False, and the group has no inversion 
        symmetry, additional lines are returned.

    :param reference_distance: a reference target distance between neighboring
        k-points in the path, in units of 1/ang. The actual value will be as
        close as possible to this value, to have an integer number of points in
        each path.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:
       'hpkot': HPKOT paper: 
       Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure 
       diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
       DOI: 10.1016/j.commatsci.2016.10.015

    :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI lattice, if abs(a-c) < threshold, a EdgeCaseWarning is issued.
        Note that depending on the bravais lattice, the meaning of the 
        threshold is different (angle, length, ...)

    :return: a dictionary with the following 
        keys:

        - has_inversion_symmetry: True or False, depending on whether the
          input crystal structure has inversion symmetry or not.
        - augmented_path: if True, it means that the path was
          augmented with the -k points (this happens if both 
          has_inversion_symmetry is False, and the user set 
          with_time_reversal=False in the input)
        - primitive_structure: the StructureData for the primitive cell
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the crystallographic primitive cell 
        - explicit_kpoints: An AiiDA KPointsData object (without weights)
          with the kpoints and the respective labels.
          For each segment, the two endpoints are always included, 
          independently of the length.
        - explicit_kpoints_linearcoord: array of floats, giving the 
          coordinate at which to plot the corresponding point.
        - segments: a list of length-2 tuples, with the start and end index
          of each segment. **Note**! The indices are supposed to be used as 
          follows: the labels for the i-th segment are given by::

            segment_indices = segments[i]
            segment_points = explicit_kpoints.get_kpoints[slice(*segment_indices)]

          This means, in particular, that if you want the label of the start
          and end points, you should do::

            start_point = explicit_kpoints.get_kpoints[segment_indices[0]]
            stop_point = explicit_kpoints.get_kpoints[segment_indices[1]-1]

          (note the minus one!)

          Also, note that if segments[i-1][1] == segments[i][0] + 1 it means
          that the point was calculated only once, and it belongs to both 
          paths. Instead, if segments[i-1][1] == segments[i][0], then
          this is a 'break' point in the path (e.g., segments[i-1][1] is the
          X point, and segments[i][0] is the R point, and typically in a 
          graphical representation they are shown at the same coordinate, 
          with a label "R|X").
    """
    import warnings
    warnings.warn(
        'this method has been deprecated and moved to AiiDA, see {}'.format(
            DEPRECATION_DOCS_URL), DeprecationWarning)

    import copy
    from aiida.orm import DataFactory

    struc_tuple, kind_info, kinds = _aiida_to_tuple(structure)

    retdict = _raw_explicit_path(struc_tuple)

    # Replace primitive structure with AiiDA StructureData
    primitive_lattice = retdict.pop('primitive_lattice')
    primitive_positions = retdict.pop('primitive_positions')
    primitive_types = retdict.pop('primitive_types')
    primitive_tuple = (primitive_lattice, primitive_positions, primitive_types)
    primitive_structure = _tuple_to_aiida(primitive_tuple, kind_info, kinds)
    retdict['primitive_structure'] = primitive_structure

    # Remove reciprocal_primitive_lattice, recalculated by kpoints class
    retdict.pop('reciprocal_primitive_lattice')
    KpointsData = DataFactory('array.kpoints')
    kpoints_abs = retdict.pop('explicit_kpoints_abs')
    kpoints_rel = retdict.pop('explicit_kpoints_rel')
    kpoints_labels = retdict.pop('explicit_kpoints_labels')
    # Expects something of the type [[0,'X'],[34,'L'],...]
    # So I generate it, skipping empty labels
    labels = [[idx, label] for idx, label in enumerate(kpoints_labels) if label]

    kpoints = KpointsData()
    kpoints.set_cell_from_structure(primitive_structure)
    kpoints.set_kpoints(kpoints_abs, cartesian=True, labels=labels)
    retdict['explicit_kpoints'] = kpoints

    return retdict


def get_path(structure,
             with_time_reversal=True,
             reference_distance=0.025,
             recipe='hpkot',
             threshold=1.e-7):
    """
    Return the kpoint path information for band structure given a 
    crystal structure, using the paths from the chosen recipe/reference.
    The parameters are the same
    as get get_path in __init__, but here all structures are
    input and returned as AiiDA structures rather than tuples.

    If you use this module, please cite the paper of the corresponding 
    recipe (see parameter below).

    .. deprecated:: 1.8
      Use the methods in AiiDA instead.

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be an AiiDA StructureData object.

    :param with_time_reversal: if False, and the group has no inversion 
        symmetry, additional lines are returned as described in the HPKOT
        paper.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:
       'hpkot': HPKOT paper: 
       Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure 
       diagram paths based on crystallography, Comp. Mat. Sci. 128, 140 (2017).
       DOI: 10.1016/j.commatsci.2016.10.015

   :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI lattice, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
        Note that depending on the bravais lattice, the meaning of the 
        threshold is different (angle, length, ...)

    :return: a dictionary with the following 
      keys:

        - point_coords: a dictionary with label -> float coordinates
        - path: a list of length-2 tuples, with the labels of the starting
          and ending point of each label section
        - has_inversion_symmetry: True or False, depending on whether the
          input crystal structure has inversion symmetry or not.
        - augmented_path: if True, it means that the path was
          augmented with the -k points (this happens if both 
          has_inversion_symmetry is False, and the user set 
          with_time_reversal=False in the input)
        - bravais_lattice: the Bravais lattice string (like 'cP', 'tI', ...)
        - bravais_lattice_extended: the specific case used to define labels and
          coordinates (like 'cP1', 'tI2', ...)
        - conv_structure: AiiDA StructureData for the crystallographic conventional 
          cell 
        - primitive_structure: AiiDA StructureData for the crystallographic primitive 
          cell 
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - primitive_transformation_matrix: the transformation matrix P between
          the conventional and the primitive cell 
        - inverse_primitive_transformation_matrix: the inverse of the matrix P
          (the determinant is integer and gives the ratio in volume between
          the conventional and primitive cells)
        - volume_original_wrt_conv: volume ratio of the user-provided cell
          with respect to the the crystallographic conventional cell 
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the crystallographic primitive cell 

    :note: An EdgeCaseWarning is issued for edge cases (e.g. if a==b==c for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    import warnings
    warnings.warn(
        'this method has been deprecated and moved to AiiDA, see {}'.format(
            DEPRECATION_DOCS_URL), DeprecationWarning)

    import copy
    from aiida.orm import DataFactory

    struc_tuple, kind_info, kinds = _aiida_to_tuple(structure)

    retdict = _raw_get_path(struc_tuple)

    # Replace conv structure with AiiDA StructureData
    conv_lattice = retdict.pop('conv_lattice')
    conv_positions = retdict.pop('conv_positions')
    conv_types = retdict.pop('conv_types')
    conv_tuple = (conv_lattice, conv_positions, conv_types)
    conv_structure = _tuple_to_aiida(conv_tuple, kind_info, kinds)
    retdict['conv_structure'] = conv_structure

    # Replace primitive structure with AiiDA StructureData
    primitive_lattice = retdict.pop('primitive_lattice')
    primitive_positions = retdict.pop('primitive_positions')
    primitive_types = retdict.pop('primitive_types')
    primitive_tuple = (primitive_lattice, primitive_positions, primitive_types)
    primitive_structure = _tuple_to_aiida(primitive_tuple, kind_info, kinds)
    retdict['primitive_structure'] = primitive_structure

    return retdict
