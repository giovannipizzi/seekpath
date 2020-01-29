from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
import unittest
from .util import atoms_num_dict


def simple_read_poscar(fname):
    with open(fname) as f:
        lines = [l.partition('!')[0] for l in f.readlines()]

    alat = float(lines[1])
    v1 = [float(_) * alat for _ in lines[2].split()]
    v2 = [float(_) * alat for _ in lines[3].split()]
    v3 = [float(_) * alat for _ in lines[4].split()]
    cell = [v1, v2, v3]

    species = lines[5].split()
    num_atoms = [int(_) for _ in lines[6].split()]

    next_line = lines[7]
    if next_line.strip().lower() != 'direct':
        raise ValueError(
            "This simple routine can only deal with 'direct' POSCARs")
    # Note: to support also cartesian, remember to multiply the coordinates
    # by alat

    positions = []
    atomic_numbers = []
    cnt = 8
    for el, num in zip(species, num_atoms):
        atom_num = atoms_num_dict[el.capitalize()]
        for at_idx in range(num):
            atomic_numbers.append(atom_num)
            positions.append([float(_) for _ in lines[cnt].split()])
            cnt += 1

    return (cell, positions, atomic_numbers)


class TestPaths3D_HPKOT_Supercell(unittest.TestCase):
    """
    Test what happens for a supercell
    """

    def test_supercell(self):
        """
        Test a supercell (BCC).
        This is just a very basic test.
        """
        from seekpath import hpkot

        cell = [[4., 0., 0.], [0., 10., 0.], [0., 0., 4.]]
        positions = [[0., 0., 0.], [0.5, 0.25, 0.5], [0., 0.5, 0.],
                     [0.5, 0.75, 0.5]]
        atomic_numbers = [6, 6, 6, 6]

        system = (cell, positions, atomic_numbers)
        res = hpkot.get_path(system, with_time_reversal=False)

        # Just some basic checks...
        self.assertEqual(res['volume_original_wrt_conv'], 2)
        self.assertEqual(res['volume_original_wrt_prim'], 4)


class TestSpglibSymprec(unittest.TestCase):
    """
    Tests to check if the symprec is properly passed
    """

    def basic_test(self,
                   cell,
                   positions,
                   atomic_numbers,
                   check_bravais_lattice,
                   symprec=None):
        """
        Given a cell, the positions and the atomic numbers, checks
        that the bravais lattice is the expected one.

        :param cell: 3x3 list of lattice vectors
        :param positions: Nx3 list of (scaled) positions
        :param atomic_number: list of length N with the atomic numbers
        :param check_bravais_lattice: a string with the expected Bravais lattice 
            (e.g., 'tI', 'oF', ...)
        :param symprec: if specified, pass also the symprec to the code
        """
        import warnings

        from seekpath import hpkot

        system = (cell, positions, atomic_numbers)

        if symprec is None:
            res = hpkot.get_path(system, with_time_reversal=False)
        else:
            res = hpkot.get_path(system,
                                 with_time_reversal=False,
                                 symprec=symprec)
        # Checks
        self.assertEqual(res['bravais_lattice'], check_bravais_lattice)

    def test_symprec(self):
        """
        Test the edge case for tI.
        """
        cell = [[4., 0., 0.], [0., 4., 0.], [0., 0., 4.00001]]
        positions = [[0., 0., 0.]]
        atomic_numbers = [6]

        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='tP',
                        symprec=1.e-8)

        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='cP',
                        symprec=1.e-3)


class TestExplicitPaths(unittest.TestCase):

    def test_keys(self):
        """
        Test the edge case for tI.
        """
        import seekpath

        cell = [[4., 0., 0.], [0., 4., 0.], [0., 0., 4.]]
        positions = [[0., 0., 0.], [0.5, 0.5, 0.5]]
        atomic_numbers = [6, 6]

        system = (cell, positions, atomic_numbers)

        res = seekpath.get_explicit_k_path(system, recipe='hpkot')

        known_keys = set([
            'augmented_path', 'bravais_lattice', 'bravais_lattice_extended',
            'conv_lattice', 'conv_positions', 'conv_types',
            'explicit_kpoints_abs', 'explicit_kpoints_labels',
            'explicit_kpoints_linearcoord', 'explicit_kpoints_rel',
            'explicit_segments', 'has_inversion_symmetry',
            'inverse_primitive_transformation_matrix', 'path', 'point_coords',
            'primitive_lattice', 'primitive_positions',
            'primitive_transformation_matrix', 'primitive_types',
            'reciprocal_primitive_lattice', 'spacegroup_international',
            'spacegroup_number', 'volume_original_wrt_conv',
            'volume_original_wrt_prim'
        ])

        missing_known_keys = known_keys - set(res.keys())
        if missing_known_keys:
            raise AssertionError("Some keys are not returned from the "
                                 "get_explicit_k_path function: {}".format(
                                     ', '.join(missing_known_keys)))


class TestPaths3D_HPKOT_EdgeCases(unittest.TestCase):
    """
    Test the warnings issued for edge cases
    """

    def basic_test(self,
                   cell,
                   positions,
                   atomic_numbers,
                   check_bravais_lattice,
                   check_string=None,
                   symprec=None):
        """
        Given a cell, the positions and the atomic numbers, checks that
        (only one) warning is issued, of type hpkot.EdgeCaseWarning,
        that the bravais lattice is the expected one,
        and that (optionally, if specified) the warning message contains
        the given string 'check_string'.

        :param cell: 3x3 list of lattice vectors
        :param positions: Nx3 list of (scaled) positions
        :param atomic_number: list of length N with the atomic numbers
        :param check_bravais_lattice: a string with the expected Bravais lattice 
            (e.g., 'tI', 'oF', ...)
        :param check_string: if specified, this should be contained in the warning
            message
        :param symprec: if specified, pass also the symprec to the code
        """
        import warnings

        from seekpath import hpkot

        system = (cell, positions, atomic_numbers)

        with warnings.catch_warnings(record=True) as w:
            if symprec is None:
                res = hpkot.get_path(system, with_time_reversal=False)
            else:
                res = hpkot.get_path(system,
                                     with_time_reversal=False,
                                     symprec=symprec)
            # Checks
            self.assertEqual(res['bravais_lattice'], check_bravais_lattice)
            # Checks on issued warnings
            relevant_w = [
                _ for _ in w if issubclass(_.category, hpkot.EdgeCaseWarning)
            ]
            self.assertEqual(
                len(relevant_w), 1, 'Wrong number of warnings issued! '
                '({} instead of 1)'.format(len(relevant_w)))
            if check_string is not None:
                self.assertIn(check_string, str(relevant_w[0].message))

    def test_tI(self):
        """
        Test the edge case for tI.
        """
        cell = [[4., 0., 0.], [0., 4., 0.], [0., 0., 4.]]
        positions = [[0., 0., 0.], [0.5, 0.5, 0.5], [0.0, 0.0, 0.1],
                     [0.5, 0.5, 0.6]]
        atomic_numbers = [6, 6, 8, 8]

        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='tI')

    def test_oF_first(self):
        from math import sqrt

        cell = [[sqrt(1. / (1 / 16. + 1 / 25.)), 0., 0.], [0., 4., 0.],
                [0., 0., 5.]]
        positions = [[0., 0., 0.], [0., 0.5, 0.5], [0.5, 0., 0.5],
                     [0.5, 0.5, 0.]]
        atomic_numbers = [6, 6, 6, 6]
        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='oF',
                        check_string="but 1/a^2")

    def test_oF_second(self):
        from math import sqrt

        cell = [[10, 0, 0], [0, 21, 0],
                [0, 0, sqrt(1. / (1 / 100. + 1 / 441.))]]
        positions = [
            [0.1729328200000002, 0.5632488700000001, 0.9531259500000002],
            [0.8270671799999998, 0.4367511299999999, 0.9531259500000002],
            [0.0770671799999998, 0.3132488700000001, 0.7031259500000002],
            [0.9229328200000002, 0.6867511299999999, 0.7031259500000002],
            [0.1729328200000002, 0.0632488700000001, 0.4531259500000002],
            [0.8270671799999998, 0.9367511299999998, 0.4531259500000002],
            [0.0770671799999998, 0.8132488700000001, 0.2031259500000002],
            [0.9229328200000002, 0.1867511299999999, 0.2031259500000002],
            [0.6729328200000002, 0.5632488700000001, 0.4531259500000002],
            [0.3270671799999998, 0.4367511299999999, 0.4531259500000002],
            [0.5770671799999998, 0.3132488700000001, 0.2031259500000002],
            [0.4229328200000002, 0.6867511299999999, 0.2031259500000002],
            [0.6729328200000002, 0.0632488700000001, 0.9531259500000002],
            [0.3270671799999998, 0.9367511299999998, 0.9531259500000002],
            [0.5770671799999998, 0.8132488700000001, 0.7031259500000002],
            [0.4229328200000002, 0.1867511299999999, 0.7031259500000002],
            [0.0000000000000000, 0.5000000000000000, 0.4701481000000003],
            [0.7500000000000000, 0.7500000000000000, 0.2201481000000003],
            [0.0000000000000000, 0.0000000000000000, 0.9701481000000002],
            [0.7500000000000000, 0.2500000000000000, 0.7201481000000003],
            [0.5000000000000000, 0.5000000000000000, 0.9701481000000002],
            [0.2500000000000000, 0.7500000000000000, 0.7201481000000003],
            [0.5000000000000000, 0.0000000000000000, 0.4701481000000003],
            [0.2500000000000000, 0.2500000000000000, 0.2201481000000003]
        ]
        atomic_numbers = [6] * 16 + [8] * 8
        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='oF',
                        check_string="but 1/c^2")

    def test_oI_bc(self):

        cell = [[4., 0., 0.], [0., 5., 0.], [0., 0., 5.]]
        positions = [[0., 0., 0.], [0.5, 0.5, 0.5], [0., 0., 0.1],
                     [0.5, 0.5, 0.6]]
        atomic_numbers = [6, 6, 8, 8]
        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='oI',
                        check_string="but the two longest vectors b and c")

    def test_oC(self):

        cell = [[3., 0., 0.], [0., 3., 0.], [0., 0., 5.]]
        positions = [
            [0.5000000000000000, 0.1136209299999999, 0.7500967299999999],
            [0.5000000000000000, 0.8863790700000000, 0.2500967299999999],
            [0.0000000000000000, 0.6136209300000000, 0.7500967299999999],
            [0.0000000000000000, 0.3863790700000001, 0.2500967299999999],
            [0.0000000000000000, 0.8444605049999999, 0.7659032699999999],
            [0.0000000000000000, 0.1555394950000001, 0.2659032699999999],
            [0.5000000000000000, 0.3444605049999999, 0.7659032699999999],
            [0.5000000000000000, 0.6555394950000001, 0.2659032699999999]
        ]
        atomic_numbers = [6, 6, 6, 6, 8, 8, 8, 8]
        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='oC')

    def test_oA(self):

        cell = [[9., 0., 0.], [0., 3., 0.], [0., 0., 3.]]
        positions = [
            [0.0000000000000000, 0.0000000000000000, 0.0309652399999998],
            [0.0000000000000000, 0.5000000000000000, 0.5309652399999998],
            [0.0000000000000000, 0.5000000000000000, 0.8489601849999999],
            [0.5000000000000000, 0.5000000000000000, 0.1263269549999999],
            [0.0000000000000000, 0.0000000000000000, 0.3489601849999999],
            [0.5000000000000000, 0.0000000000000000, 0.6263269549999999]
        ]
        atomic_numbers = [6, 6, 8, 8, 8, 8]
        self.basic_test(cell,
                        positions,
                        atomic_numbers,
                        check_bravais_lattice='oA')

    # For full coverage, we should also implement the tests for the warnings
    # in the mC lattices, and for the oP warnings.


class TestPaths3D_HPKOT(unittest.TestCase):
    """
    Class to test the creation of paths for all cases using example structures
    """
    # If True, print on stdout the band paths
    verbose_tests = False

    def base_test(self, ext_bravais, with_inv):
        """
        Test a specific extended Bravais symol, 
        with or without inversion (uses the cell whose
        POSCAR is stored in the directories - they have been obtained by 
        Y. Hinuma from the Materials Project).

        :param ext_bravais: a string with the extended Bravais Lattice symbol 
           (like 'cF1', for instance)
        :param with_inv: if True, consider a system with inversion symmetry,
            otherwise one without (in which case, the get_path function is
            called with the kwarg 'with_time_reversal = False')
        """
        import os

        from seekpath import hpkot

        # Get the POSCAR with the example structure
        this_folder = os.path.split(os.path.abspath(hpkot.__file__))[0]
        folder = os.path.join(this_folder, "band_path_data", ext_bravais)
        poscar_with_inv = os.path.join(folder, 'POSCAR_inversion')
        poscar_no_inv = os.path.join(folder, 'POSCAR_noinversion')

        poscar = poscar_with_inv if with_inv else poscar_no_inv
        #asecell = ase.io.read(poscar)
        # system = (asecell.get_cell(), asecell.get_scaled_positions(),
        #    asecell.get_atomic_numbers())
        system = simple_read_poscar(poscar)

        res = hpkot.get_path(system, with_time_reversal=False)

        self.assertEqual(res['bravais_lattice_extended'], ext_bravais)
        self.assertEqual(res['has_inversion_symmetry'], with_inv)

        if self.verbose_tests:
            print("*** {} (inv={})".format(ext_bravais, with_inv))
            for p1, p2 in res['path']:
                print("   {} -- {}: {} -- {}".format(p1, p2,
                                                     res['point_coords'][p1],
                                                     res['point_coords'][p2]))

    def test_aP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) aP2.
        """
        self.base_test(ext_bravais="aP2", with_inv=True)

    def test_aP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) aP2.
        """
        self.base_test(ext_bravais="aP2", with_inv=False)

    def test_aP3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) aP3.
        """
        self.base_test(ext_bravais="aP3", with_inv=True)

    def test_aP3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) aP3.
        """
        self.base_test(ext_bravais="aP3", with_inv=False)

    def test_cF1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) cF1.
        """
        self.base_test(ext_bravais="cF1", with_inv=True)

    def test_cF1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) cF1.
        """
        self.base_test(ext_bravais="cF1", with_inv=False)

    def test_cF2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) cF2.
        """
        self.base_test(ext_bravais="cF2", with_inv=True)

    def test_cF2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) cF2.
        """
        self.base_test(ext_bravais="cF2", with_inv=False)

    def test_cI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) cI1.
        """
        self.base_test(ext_bravais="cI1", with_inv=True)

    def test_cI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) cI1.
        """
        self.base_test(ext_bravais="cI1", with_inv=False)

    def test_cP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) cP1.
        """
        self.base_test(ext_bravais="cP1", with_inv=True)

    def test_cP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) cP1.
        """
        self.base_test(ext_bravais="cP1", with_inv=False)

    def test_cP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) cP2.
        """
        self.base_test(ext_bravais="cP2", with_inv=True)

    def test_cP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) cP2.
        """
        self.base_test(ext_bravais="cP2", with_inv=False)

    def test_hP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) hP1.
        """
        self.base_test(ext_bravais="hP1", with_inv=True)

    def test_hP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) hP1.
        """
        self.base_test(ext_bravais="hP1", with_inv=False)

    def test_hP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) hP2.
        """
        self.base_test(ext_bravais="hP2", with_inv=True)

    def test_hP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) hP2.
        """
        self.base_test(ext_bravais="hP2", with_inv=False)

    def test_hR1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) hR1.
        """
        self.base_test(ext_bravais="hR1", with_inv=True)

    def test_hR1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) hR1.
        """
        self.base_test(ext_bravais="hR1", with_inv=False)

    def test_hR2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) hR2.
        """
        self.base_test(ext_bravais="hR2", with_inv=True)

    def test_hR2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) hR2.
        """
        self.base_test(ext_bravais="hR2", with_inv=False)

    def test_mC1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) mC1.
        """
        self.base_test(ext_bravais="mC1", with_inv=True)

    def test_mC1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) mC1.
        """
        self.base_test(ext_bravais="mC1", with_inv=False)

    def test_mC2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) mC2.
        """
        self.base_test(ext_bravais="mC2", with_inv=True)

    def test_mC2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) mC2.
        """
        self.base_test(ext_bravais="mC2", with_inv=False)

    def test_mC3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) mC3.
        """
        self.base_test(ext_bravais="mC3", with_inv=True)

    def test_mC3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) mC3.
        """
        self.base_test(ext_bravais="mC3", with_inv=False)

    def test_mP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) mP1.
        """
        self.base_test(ext_bravais="mP1", with_inv=True)

    def test_mP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) mP1.
        """
        self.base_test(ext_bravais="mP1", with_inv=False)

# oA1Y does not exist by symmetry
#    def test_oA1Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        Bravais lattice (extended) oA1.
#        """
#        self.base_test(ext_bravais="oA1", with_inv = True)

    def test_oA1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oA1.
        """
        self.base_test(ext_bravais="oA1", with_inv=False)

# oA2Y does not exist by symmetry
#    def test_oA2Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        Bravais lattice (extended) oA2.
#        """
#        self.base_test(ext_bravais="oA2", with_inv = True)

    def test_oA2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oA2.
        """
        self.base_test(ext_bravais="oA2", with_inv=False)

    def test_oC1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oC1.
        """
        self.base_test(ext_bravais="oC1", with_inv=True)

    def test_oC1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oC1.
        """
        self.base_test(ext_bravais="oC1", with_inv=False)

    def test_oC2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oC2.
        """
        self.base_test(ext_bravais="oC2", with_inv=True)

    def test_oC2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oC2.
        """
        self.base_test(ext_bravais="oC2", with_inv=False)

    def test_oF1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oF1.
        """
        self.base_test(ext_bravais="oF1", with_inv=True)

    def test_oF1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oF1.
        """
        self.base_test(ext_bravais="oF1", with_inv=False)

# oF2Y does not exist by symmetry
#    def test_oF2Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        Bravais lattice (extended) oF2.
#        """
#        self.base_test(ext_bravais="oF2", with_inv = True)

    def test_oF2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oF2.
        """
        self.base_test(ext_bravais="oF2", with_inv=False)

    def test_oF3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oF3.
        """
        self.base_test(ext_bravais="oF3", with_inv=True)

    def test_oF3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oF3.
        """
        self.base_test(ext_bravais="oF3", with_inv=False)

    def test_oI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oI1.
        """
        self.base_test(ext_bravais="oI1", with_inv=True)

    def test_oI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oI1.
        """
        self.base_test(ext_bravais="oI1", with_inv=False)


# oI2Y does not exist by symmetry
#    def test_oI2Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        Bravais lattice (extended) oI2.
#        """
#        self.base_test(ext_bravais="oI2", with_inv=True)

    def test_oI2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oI2.
        """
        self.base_test(ext_bravais="oI2", with_inv=False)

    def test_oI3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oI3.
        """
        self.base_test(ext_bravais="oI3", with_inv=True)

    def test_oI3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oI3.
        """
        self.base_test(ext_bravais="oI3", with_inv=False)

    def test_oP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) oP1.
        """
        self.base_test(ext_bravais="oP1", with_inv=True)

    def test_oP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) oP1.
        """
        self.base_test(ext_bravais="oP1", with_inv=False)

    def test_tI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) tI1.
        """
        self.base_test(ext_bravais="tI1", with_inv=True)

    def test_tI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) tI1.
        """
        self.base_test(ext_bravais="tI1", with_inv=False)

    def test_tI2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) tI2.
        """
        self.base_test(ext_bravais="tI2", with_inv=True)

    def test_tI2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) tI2.
        """
        self.base_test(ext_bravais="tI2", with_inv=False)

    def test_tP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        Bravais lattice (extended) tP1.
        """
        self.base_test(ext_bravais="tP1", with_inv=True)

    def test_tP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        Bravais lattice (extended) tP1.
        """
        self.base_test(ext_bravais="tP1", with_inv=False)
