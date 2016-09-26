"""
The kpath3d module contains routines to get automatically the
path in a 3D Brillouin zone to plot band structures.

Author: Giovanni Pizzi, EPFL (2016)

Licence: MIT License

Copyright (c), 2016, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE
(Theory and Simulation of Materials (THEOS) and National Centre for 
Computational Design and Discovery of Novel Materials (NCCR MARVEL)). 
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
def get_tuple_from_aiida_structure(aiida_structure):
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

    Z = {v['symbol']: k for k,v in elements.iteritems()}

    cell = np.array(aiida_structure.cell)
    abs_pos = np.array([_.position for _ in aiida_structure.sites])
    rel_pos = np.dot(abs_pos, np.linalg.inv(cell))
    kinds = {k.name: k for k in aiida_structure.kinds}
    
    kind_numbers = {}
    for kind in aiida_structure.kinds:
        if len(kind.symbols) == 1:
            realnumber = Z[kind.symbols[0]]
            if realnumber in kind_numbers.values():
                number = get_new_number(kind_numbers.values(), start_from=realnumber*1000)
            else:
                number = realnumber
            kind_numbers[kind.name] = number
        else:
            number = get_new_number(kind_numbers.values(), start_from=200000)
            kind_numbers[kind.name] = number

    numbers = [kind_numbers[s.kind_name] for s in aiida_structure.sites]

    return ((cell, rel_pos, numbers), kind_numbers, list(aiida_structure.kinds))
    
def get_aiida_structure_from_tuple(structure_tuple, kind_info=None, kinds=None):
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

    Z = {v['symbol']: k for k,v in elements.iteritems()}
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
        raise ValueError("There is at least a number repeated twice in kind_info!")
    # Invert the mapping
    mapping_num_kindname = {v: k for k, v in _kind_info.iteritems()}
    # Create the actual mapping
    try:
        mapping_to_kinds = {num: _kinds_dict[kindname] for num, kindname 
                            in mapping_num_kindname.iteritems()}
    except KeyError as e:
        raise ValueError("Unable to find '{}' in the kinds list".format(e.message))
        

    try:
        site_kinds = [mapping_to_kinds[num] for num in numbers]
    except KeyError as e:
        raise ValueError("Unable to find kind in kind_info for number {}".format(e.message))

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


def get_path(structure, with_time_reversal=True, recipe='hpkot',
             threshold=1.e-7):
    """
    Return the kpoint path information for band structure given a 
    crystal structure, using the paths from the chosen recipe/reference.

    If you use this module, please cite the paper of the corresponding 
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: (cell, positions, numbers), where 
        (if N is the number of atoms):

        - cell is a 3x3 list of floats (cell[0] is the first lattice 
          vector, ...)
        - positions is a Nx3 list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - numbers is a length-N list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but 
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

    :param with_time_reversal: if False, and the group has no inversion 
        symmetry, additional lines are returned as described in the HPKOT
        paper.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:
       'hpkot': HPKOT paper: 
       Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band structure  
       diagram paths based on crystallography, arXiv:1602.06402 (2016)

   :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI case, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
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
        - bravais_lattice_case: the specific case used to define labels and
          coordinates (like 'cP1', 'tI2', ...)
        - std_lattice: three real-space vectors for the standard conventional 
          cell (std_lattice[0,:] is the first vector)
        - std_positions: fractional coordinates of atoms in the standard 
          conventional cell 
        - std_types: list of integer types of the atoms in the standard 
          conventional cell (typically, the atomic numbers)
        - primitive_lattice: three real-space vectors for the standard primitive
          cell (primitive_lattice[0,:] is the first vector)
        - primitive_positions: fractional coordinates of atoms in the standard 
          primiitive cell 
        - primitive_types: list of integer types of the atoms in the standard 
          conventional cell (typically, the atomic numbers)
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - primitive_transformation_matrix: the transformation matrix P between
          the conventional and the primitive cell 
        - inverse_primitive_transformation_matrix: the inverse of the matrix P
          (the determinant is integer and gives the ratio in volume between
          the conventional and primitive cells)
        - volume_original_wrt_std: volume ratio of the user-provided cell
          with respect to the the standard conventional cell 
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the standard primitive cell 

    :note: An EdgeCaseWarning is issued for edge cases (e.g. if a==b==c for
        orthorhombic systems). In this case, still one of the valid cases
        is picked.
    """
    if recipe == 'hpkot':
        from . import hpkot
        res = hpkot.get_path(structure, with_time_reversal, threshold)

        return res
    else:
        raise ValueError("value for 'recipe' not recognized. The only value "
            "currently accepted is 'hpkot'.")


def get_explicit_k_path(structure, with_time_reversal=True,
    reference_distance=0.025, recipe='hpkot', 
    threshold=1.e-7):
    """
    Return the kpoint path for band structure (in scaled and absolute 
    coordinates), given a crystal structure,
    using the paths proposed in the various publications (see description
    of the 'recipe' input parameter). 
    Note that the k-path typically refers to a different unit cell
    (e.g., the primitive one with some transformation matrix to comply with
    the conventions in the case of the HPKOT paper). So, one should use the
    crystal cell provided in output for all calculations, rather than the
    input 'structure'.

    If you use this module, please cite the paper of the corresponding 
    recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be a tuple in the format
        accepted by spglib: (cell, positions, numbers), where 
        (if N is the number of atoms):

        - cell is a 3x3 list of floats (cell[0] is the first lattice 
          vector, ...)
        - positions is a Nx3 list of floats with the atomic coordinates
          in scaled coordinates (i.e., w.r.t. the cell vectors)
        - numbers is a length-N list with integers identifying uniquely
          the atoms in the cell (e.g., the Z number of the atom, but 
          any other positive non-zero integer will work - e.g. if you
          want to distinguish two Carbon atoms, you can set one number
          to 6 and the other to 1006)

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
       diagram paths based on crystallography, arXiv:1602.06402 (2016)

    :param threshold: the threshold to use to verify if we are in 
        and edge case (e.g., a tetragonal cell, but a==c). For instance, 
        in the tI case, if abs(a-c) < threshold, a EdgeCaseWarning is issued. 
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
        - primitive_lattice: three real-space vectors for the standard primitive
          cell (primitive_lattice[0,:] is the first vector)
        - primitive_positions: fractional coordinates of atoms in the standard 
          primitive cell 
        - primitive_types: list of integer types of the atoms in the standard 
          conventional cell (typically, the atomic numbers)
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the standard primitive cell 
        - explicit_kpoints_abs: List of the kpoints along the specific path in 
          absolute (Cartesian) coordinates. The two endpoints are always 
          included, independently of the length.
        - explicit_kpoints_rel: List of the kpoints along the specific path in 
          relative (fractional) coordinates (same length as 
          explicit_kpoints_abs).
        - explicit_kpoints_labels: list of strings with kpoints labels. It has 
          the same length as explicit_kpoints_abs and explicit_kpoints_rel. 
          Empty if the point is not a special point.
        - explicit_kpoints_linearcoord: array of floats, giving the coordinate 
          at which to plot the corresponding point.
        - segments: a list of length-2 tuples, with the start and end 
          index of each segment. **Note**! The indices are supposed to be 
          used as follows: the labels for the i-th segment are given by::

            segment_indices = segments[i]
            segment_labels = explicit_kpoints_labels[slice(*segment_indices)]

          This means, in particular, that if you want the label of the start
          and end points, you should do::

            start_label = explicit_kpoints_labels[segment_indices[0]]
            stop_label = explicit_kpoints_labels[segment_indices[1]-1]

          (note the minus one!)

          Also, note that if 
          ``segments[i-1][1] == segments[i][0] + 1`` it means
          that the point was calculated only once, and it belongs to both 
          paths. Instead, if 
          ``segments[i-1][1] == segments[i][0]``, then
          this is a 'break' point in the path (e.g., ``segments[i-1][1]``
          is the X point, and ``segments[i][0]`` is the R point, 
          and typically in a graphical representation they are shown at the 
          same coordinate, with a label "R|X").
    """
    import numpy as np

    if recipe == 'hpkot':
        from . import hpkot
        res = hpkot.get_path(structure, with_time_reversal, threshold)

        retdict = {}
        retdict['has_inversion_symmetry'] = res['has_inversion_symmetry']
        retdict['augmented_path'] = res['augmented_path']
        retdict['primitive_lattice'] = res['primitive_lattice']
        retdict['primitive_positions'] = res['primitive_positions']
        retdict['primitive_types'] = res['primitive_types']
        retdict['reciprocal_primitive_lattice'] = res[
            'reciprocal_primitive_lattice']
        retdict['volume_original_wrt_prim'] = res[
            'volume_original_wrt_prim']

        kpoints_rel = []
        kpoints_labels = []
        kpoints_linearcoord = []
        previous_linearcoord = 0.
        segments = []
        for start_label, stop_label in res['path']:
            start_coord = np.array(res['point_coords'][start_label])
            stop_coord = np.array(res['point_coords'][stop_label])
            start_coord_abs = np.dot(start_coord, 
                retdict['reciprocal_primitive_lattice'])
            stop_coord_abs = np.dot(stop_coord, 
                retdict['reciprocal_primitive_lattice'])
            segment_length = np.linalg.norm(stop_coord_abs - start_coord_abs)
            num_points = max(2, int(segment_length / reference_distance))
            segment_linearcoord = np.linspace(0., segment_length, num_points)
            segment_start = len(kpoints_labels)
            for i in range(num_points):
                # Skip the first point if it's the same as the last one of 
                # the previous segment
                if i == 0:
                    if kpoints_labels:
                        if kpoints_labels[-1] == start_label:
                            segment_start -= 1
                            continue

                kpoints_rel.append(start_coord + 
                    (stop_coord - start_coord) * float(i) / float(num_points-1))
                if i == 0:
                    kpoints_labels.append(start_label)
                elif i == num_points - 1:
                    kpoints_labels.append(stop_label)
                else:
                    kpoints_labels.append('')
                kpoints_linearcoord.append(
                    previous_linearcoord + segment_linearcoord[i])
            previous_linearcoord += segment_length
            segment_end = len(kpoints_labels)
            segments.append((segment_start, segment_end))

        retdict['explicit_kpoints_rel'] = np.array(kpoints_rel)
        retdict['explicit_kpoints_linearcoord'] = np.array(kpoints_linearcoord)
        retdict['explicit_kpoints_labels'] = kpoints_labels
        retdict['explicit_kpoints_abs'] = np.dot(
            retdict['explicit_kpoints_rel'], 
            retdict['reciprocal_primitive_lattice'])
        retdict['segments'] = segments

        return retdict
    else:
        raise ValueError("value for 'recipe' not recognized. The only value "
            "currently accepted is 'hpkot'.")

