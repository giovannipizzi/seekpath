from . import (
    get_tuple_from_aiida_structure as _aiida_to_tuple, 
    get_aiida_structure_from_tuple as _tuple_to_aiida, 
    get_explicit_k_path as _raw_explicit_path,
    get_path as _raw_get_path)

def get_explicit_k_path(structure, with_time_reversal=True,
    reference_distance=0.025, recipe='hkot', 
    threshold=1.e-7):
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

    :param with_time_reversal: if False, and the group has no inversion 
        symmetry, additional lines are returned.

    :param reference_distance: a reference target distance between neighboring
        k-points in the path, in units of 1/ang. The actual value will be as
        close as possible to this value, to have an integer number of points in
        each path.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:
       'hkot': HKOT paper: 
       Y. Hinuma, Y Kumagai, F. Oba, I. Tanaka, Band structure diagram 
       paths based on crystallography, arXiv:1602.06402 (2016)

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
        - primitive_structure: the StructureData for the primitive cell
        - reciprocal_primitive_lattice: reciprocal-cell vectors for the 
          primitive cell (vectors are rows: reciprocal_primitive_lattice[0,:] 
          is the first vector)
        - volume_original_wrt_prim: volume ratio of the user-provided cell
          with respect to the the standard primitive cell 
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
    labels = [[idx, label] for idx, label in enumerate(kpoints_labels) 
              if label]

    kpoints = KpointsData()
    kpoints.set_cell_from_structure(primitive_structure)
    kpoints.set_kpoints(
        kpoints_abs, cartesian=True, labels=labels)
    retdict['explicit_kpoints'] = kpoints

    return retdict
    
def get_path(structure, with_time_reversal=True,
    reference_distance=0.025, recipe='hkot', 
    threshold=1.e-7):
    """
    Return the kpoint path information for band structure given a 
    crystal structure, using the paths from the chosen recipe/reference.
    The parameters are the same
    as get get_path in __init__, but here all structures are
    input and returned as AiiDA structures rather than tuples.


    If you use this module, please cite both the AiiDA paper for 
    the implementation::

      G. Pizzi et al., Comp. Mat. Sci. 111, 218 (2016),

    and the paper of the corresponding recipe (see parameter below).

    :param structure: The crystal structure for which we want to obtain
        the suggested path. It should be an AiiDA StructureData object.

    :param with_time_reversal: if False, and the group has no inversion 
        symmetry, additional lines are returned as described in the HKOT
        paper.

    :param recipe: choose the reference publication that defines the special
       points and paths.
       Currently, the following value is implemented:
       'hkot': HKOT paper: 
       Y. Hinuma, Y Kumagai, F. Oba, I. Tanaka, Band structure diagram 
       paths based on crystallography, arXiv:1602.06402 (2016)

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
        - std_structure: AiiDA StructureData for the standard conventional 
          cell 
        - primitive_structure: AiiDA StructureData for the standard primitive 
          cell 
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
    import copy
    from aiida.orm import DataFactory

    struc_tuple, kind_info, kinds = _aiida_to_tuple(structure)
    
    retdict = _raw_get_path(struc_tuple)

    # Replace std structure with AiiDA StructureData
    std_lattice = retdict.pop('std_lattice')
    std_positions = retdict.pop('std_positions')
    std_types = retdict.pop('std_types')
    std_tuple = (std_lattice, std_positions, std_types)
    std_structure = _tuple_to_aiida(std_tuple, kind_info, kinds)
    retdict['std_structure'] = std_structure

    # Replace primitive structure with AiiDA StructureData
    primitive_lattice = retdict.pop('primitive_lattice')
    primitive_positions = retdict.pop('primitive_positions')
    primitive_types = retdict.pop('primitive_types')
    primitive_tuple = (primitive_lattice, primitive_positions, primitive_types)
    primitive_structure = _tuple_to_aiida(primitive_tuple, kind_info, kinds)
    retdict['primitive_structure'] = primitive_structure
    
    return retdict
    
    
