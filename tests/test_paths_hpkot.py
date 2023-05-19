"""Test the HPKOT paths."""
# pylint: disable=invalid-name,too-many-public-methods
import numpy as np
import unittest
from seekpath.util import atoms_num_dict


def simple_read_poscar(fname):
    """Read a POSCAR file."""
    with open(fname) as f:
        lines = [l.partition("!")[0] for l in f.readlines()]

    alat = float(lines[1])
    v1 = [float(_) * alat for _ in lines[2].split()]
    v2 = [float(_) * alat for _ in lines[3].split()]
    v3 = [float(_) * alat for _ in lines[4].split()]
    cell = [v1, v2, v3]

    species = lines[5].split()
    num_atoms = [int(_) for _ in lines[6].split()]

    next_line = lines[7]
    if next_line.strip().lower() != "direct":
        raise ValueError("This simple routine can only deal with 'direct' POSCARs")
    # Note: to support also cartesian, remember to multiply the coordinates
    # by alat

    positions = []
    atomic_numbers = []
    cnt = 8
    for el, num in zip(species, num_atoms):
        atom_num = atoms_num_dict[el.capitalize()]
        for _ in range(num):
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

        cell = [[4.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 4.0]]
        positions = [
            [0.0, 0.0, 0.0],
            [0.5, 0.25, 0.5],
            [0.0, 0.5, 0.0],
            [0.5, 0.75, 0.5],
        ]
        atomic_numbers = [6, 6, 6, 6]

        system = (cell, positions, atomic_numbers)
        res = hpkot.get_path(system, with_time_reversal=False)

        # Just some basic checks...
        self.assertEqual(res["volume_original_wrt_conv"], 2)
        self.assertEqual(res["volume_original_wrt_prim"], 4)


class TestSpglibSymprec(unittest.TestCase):
    """
    Tests to check if the symprec is properly passed
    """

    def basic_test(
        self, cell, positions, atomic_numbers, check_bravais_lattice, symprec=None
    ):
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
        from seekpath import hpkot

        system = (cell, positions, atomic_numbers)

        if symprec is None:
            res = hpkot.get_path(system, with_time_reversal=False)
        else:
            res = hpkot.get_path(system, with_time_reversal=False, symprec=symprec)
        # Checks
        self.assertEqual(res["bravais_lattice"], check_bravais_lattice)

    def test_symprec(self):
        """
        Test the edge case for tI.
        """
        cell = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.00001]]
        positions = [[0.0, 0.0, 0.0]]
        atomic_numbers = [6]

        self.basic_test(
            cell, positions, atomic_numbers, check_bravais_lattice="tP", symprec=1.0e-8
        )

        self.basic_test(
            cell, positions, atomic_numbers, check_bravais_lattice="cP", symprec=1.0e-3
        )


class TestExplicitPaths(unittest.TestCase):
    """Test the creation of explicit paths."""

    def test_keys(self):  # pylint: disable=no-self-use
        """
        Test the edge case for tI.
        """
        import seekpath

        cell = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
        positions = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
        atomic_numbers = [6, 6]

        system = (cell, positions, atomic_numbers)

        res = seekpath.get_explicit_k_path(system, recipe="hpkot")

        known_keys = set(
            [
                "augmented_path",
                "bravais_lattice",
                "bravais_lattice_extended",
                "conv_lattice",
                "conv_positions",
                "conv_types",
                "explicit_kpoints_abs",
                "explicit_kpoints_labels",
                "explicit_kpoints_linearcoord",
                "explicit_kpoints_rel",
                "explicit_segments",
                "has_inversion_symmetry",
                "inverse_primitive_transformation_matrix",
                "path",
                "point_coords",
                "primitive_lattice",
                "primitive_positions",
                "primitive_transformation_matrix",
                "primitive_types",
                "reciprocal_primitive_lattice",
                "spacegroup_international",
                "spacegroup_number",
                "volume_original_wrt_conv",
                "volume_original_wrt_prim",
            ]
        )

        missing_known_keys = known_keys - set(res.keys())
        if missing_known_keys:
            raise AssertionError(
                "Some keys are not returned from the "
                "get_explicit_k_path function: {}".format(", ".join(missing_known_keys))
            )


class TestPaths3D_HPKOT_EdgeCases(unittest.TestCase):
    """
    Test the warnings issued for edge cases
    """

    def basic_test(
        self,
        cell,
        positions,
        atomic_numbers,
        check_bravais_lattice,
        check_string=None,
        symprec=None,
    ):
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
                res = hpkot.get_path(system, with_time_reversal=False, symprec=symprec)
            # Checks
            self.assertEqual(res["bravais_lattice"], check_bravais_lattice)
            # Checks on issued warnings
            relevant_w = [_ for _ in w if issubclass(_.category, hpkot.EdgeCaseWarning)]
            self.assertEqual(
                len(relevant_w),
                1,
                "Wrong number of warnings issued! "
                "({} instead of 1)".format(len(relevant_w)),
            )
            if check_string is not None:
                self.assertIn(check_string, str(relevant_w[0].message))

    def test_tI(self):
        """
        Test the edge case for tI.
        """
        cell = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
        positions = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 0.0, 0.1], [0.5, 0.5, 0.6]]
        atomic_numbers = [6, 6, 8, 8]

        self.basic_test(cell, positions, atomic_numbers, check_bravais_lattice="tI")

    def test_oF_first(self):
        """Test oF case."""
        from math import sqrt

        cell = [
            [sqrt(1.0 / (1 / 16.0 + 1 / 25.0)), 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 5.0],
        ]
        positions = [[0.0, 0.0, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]]
        atomic_numbers = [6, 6, 6, 6]
        self.basic_test(
            cell,
            positions,
            atomic_numbers,
            check_bravais_lattice="oF",
            check_string="but 1/a^2",
        )

    def test_oF_second(self):
        """Test oF case."""
        from math import sqrt

        cell = [[10, 0, 0], [0, 21, 0], [0, 0, sqrt(1.0 / (1 / 100.0 + 1 / 441.0))]]
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
            [0.2500000000000000, 0.2500000000000000, 0.2201481000000003],
        ]
        atomic_numbers = [6] * 16 + [8] * 8
        self.basic_test(
            cell,
            positions,
            atomic_numbers,
            check_bravais_lattice="oF",
            check_string="but 1/c^2",
        )

    def test_oI_bc(self):
        """Test oI case, b and c order."""
        cell = [[4.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]]
        positions = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 0.0, 0.1], [0.5, 0.5, 0.6]]
        atomic_numbers = [6, 6, 8, 8]
        self.basic_test(
            cell,
            positions,
            atomic_numbers,
            check_bravais_lattice="oI",
            check_string="but the two longest vectors b and c",
        )

    def test_oC(self):
        """Test oC case."""
        cell = [[3.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 5.0]]
        positions = [
            [0.5000000000000000, 0.1136209299999999, 0.7500967299999999],
            [0.5000000000000000, 0.8863790700000000, 0.2500967299999999],
            [0.0000000000000000, 0.6136209300000000, 0.7500967299999999],
            [0.0000000000000000, 0.3863790700000001, 0.2500967299999999],
            [0.0000000000000000, 0.8444605049999999, 0.7659032699999999],
            [0.0000000000000000, 0.1555394950000001, 0.2659032699999999],
            [0.5000000000000000, 0.3444605049999999, 0.7659032699999999],
            [0.5000000000000000, 0.6555394950000001, 0.2659032699999999],
        ]
        atomic_numbers = [6, 6, 6, 6, 8, 8, 8, 8]
        self.basic_test(cell, positions, atomic_numbers, check_bravais_lattice="oC")

    def test_oA(self):
        """Test oA case."""
        cell = [[9.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 3.0]]
        positions = [
            [0.0000000000000000, 0.0000000000000000, 0.0309652399999998],
            [0.0000000000000000, 0.5000000000000000, 0.5309652399999998],
            [0.0000000000000000, 0.5000000000000000, 0.8489601849999999],
            [0.5000000000000000, 0.5000000000000000, 0.1263269549999999],
            [0.0000000000000000, 0.0000000000000000, 0.3489601849999999],
            [0.5000000000000000, 0.0000000000000000, 0.6263269549999999],
        ]
        atomic_numbers = [6, 6, 8, 8, 8, 8]
        self.basic_test(cell, positions, atomic_numbers, check_bravais_lattice="oA")

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
        poscar_with_inv = os.path.join(folder, "POSCAR_inversion")
        poscar_no_inv = os.path.join(folder, "POSCAR_noinversion")

        poscar = poscar_with_inv if with_inv else poscar_no_inv
        # asecell = ase.io.read(poscar)
        # system = (asecell.get_cell(), asecell.get_scaled_positions(),
        #    asecell.get_atomic_numbers())
        system = simple_read_poscar(poscar)

        res = hpkot.get_path(system, with_time_reversal=False)

        self.assertEqual(res["bravais_lattice_extended"], ext_bravais)
        self.assertEqual(res["has_inversion_symmetry"], with_inv)

        if self.verbose_tests:
            print("*** {} (inv={})".format(ext_bravais, with_inv))
            for p1, p2 in res["path"]:
                print(
                    "   {} -- {}: {} -- {}".format(
                        p1, p2, res["point_coords"][p1], res["point_coords"][p2]
                    )
                )

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


class TestPaths3D_HPKOT_Orig_Cell(unittest.TestCase):
    """Test the paths for the original cell."""

    # If True, print on stdout the band paths
    verbose_tests = False

    def base_test(self, system):
        """
        Test get_path_orig_cell for given system.

        :param system: The crystal structure for which we want to test
            the suggested path. It should be a tuple in the format
            accepted by spglib: (cell, positions, numbers), where
            (if N is the number of atoms).
        """
        import os

        from seekpath import get_path, get_path_orig_cell

        res_standard = get_path(system, with_time_reversal=False, recipe="hpkot")
        res_original = get_path_orig_cell(
            system, with_time_reversal=False, recipe="hpkot"
        )
        for key in [
            "path",
            "augmented_path",
            "bravais_lattice_extended",
            "bravais_lattice",
            "bravais_lattice_extended",
            "spacegroup_number",
            "spacegroup_international",
        ]:
            self.assertEqual(res_original[key], res_standard[key])

        points_standard = res_standard["point_coords"]
        points_original = res_original["point_coords"]

        self.assertEqual(set(points_original.keys()), set(points_standard.keys()))

        # Test that the k path for the original cell in Cartesian coordinates
        # is identical to that of the standardized cell rotated by the rotation
        # matrix.
        for key in points_standard:
            k_cart_standard = (
                np.array(points_standard[key])
                @ res_standard["reciprocal_primitive_lattice"]
            )
            k_cart_standard = k_cart_standard @ res_standard["rotation_matrix"]

            reciprocal_original_lattice = np.linalg.inv(system[0]).T * 2 * np.pi
            k_cart_original = (
                np.array(points_original[key]) @ reciprocal_original_lattice
            )
            np.testing.assert_array_almost_equal(k_cart_original, k_cart_standard)

        if self.verbose_tests:
            for p1, p2 in res_original["path"]:
                print(
                    "   {} -- {}: {} -- {}".format(
                        p1,
                        p2,
                        res_original["point_coords"][p1],
                        res_original["point_coords"][p2],
                    )
                )

        return res_original

    def test_nonstandard_cubic(self):
        """
        Obtain the k-path for a non-standard cubic system.
        """
        cell = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
        positions = [[0.0, 0.0, 0.0]]
        atomic_numbers = [1]

        s = np.sin(0.3)
        c = np.cos(0.3)
        R = np.array([[-1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]])

        T = np.array([[1, 0, 1], [0, 1, 2], [0, 0, -1]])

        cell = T @ cell @ R
        positions = positions @ np.linalg.inv(T)
        system = (cell, positions, atomic_numbers)

        res = self.base_test(system)
        self.assertEqual(res["spacegroup_international"], "Pm-3m")
        self.assertEqual(res["is_supercell"], False)

    def test_nonstandard_fcc(self):
        """
        Obtain the k-path for a non-standard fcc system.
        """
        cell = [[-3.0, 0.0, 3.0], [0.0, 3.0, 3.0], [-3.0, 3.0, 0.0]]
        positions = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        atomic_numbers = [1, 1]

        s = np.sin(0.1)
        c = np.cos(0.1)
        R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])

        T = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 1]])

        cell = T @ cell @ R
        positions = positions @ np.linalg.inv(T)
        system = (cell, positions, atomic_numbers)

        res = self.base_test(system)
        self.assertEqual(res["spacegroup_international"], "Fd-3m")
        self.assertEqual(res["is_supercell"], False)

    def test_nonstandard_tetragonal(self):
        """
        Obtain the k-path for a non-standard tetragonal system, rotated by
        90 degrees to have the non-symmetric axis along x, not z.
        """
        cell = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 6.0]]
        positions = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.2]]
        atomic_numbers = [1, 2]

        R = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
        T = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])

        cell = T @ cell @ R
        positions = positions @ np.linalg.inv(T)
        system = (cell, positions, atomic_numbers)

        np.testing.assert_almost_equal(
            cell, [[6.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
        )

        res = self.base_test(system)
        self.assertEqual(res["spacegroup_international"], "P4mm")
        self.assertEqual(res["is_supercell"], False)
        np.testing.assert_almost_equal(res["point_coords"]["GAMMA"], [0.0, 0.0, 0.0])
        np.testing.assert_almost_equal(res["point_coords"]["A"], [0.5, 0.5, 0.5])
        np.testing.assert_almost_equal(res["point_coords"]["M"], [0.0, 0.5, 0.5])
        np.testing.assert_almost_equal(res["point_coords"]["R"], [0.5, 0.0, 0.5])
        np.testing.assert_almost_equal(res["point_coords"]["X"], [0.0, 0.0, 0.5])
        np.testing.assert_almost_equal(res["point_coords"]["Z"], [0.5, 0.0, 0.0])

    def test_nonstandard_monoclinic(self):
        """
        Obtain the k-path for a non-standard monoclinic system.
        """
        cell = [[1.0, 0.0, 0.0], [0.0, 3.0, 0.0], [-2.0, 0.0, 5.0]]
        positions = [[0.0, 0.0, 0.0], [0.1, 0.2, 0.3]]
        atomic_numbers = [1, 2]

        s = np.sin(-0.4)
        c = np.cos(-0.4)
        R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])

        T = np.array([[1, 2, 0], [0, 1, 0], [1, 0, 1]])

        cell = T @ cell @ R
        positions = positions @ np.linalg.inv(T)
        system = (cell, positions, atomic_numbers)

        res = self.base_test(system)
        self.assertEqual(res["spacegroup_international"], "Pm")
        self.assertEqual(res["is_supercell"], False)

    def test_nonstandard_cubic_supercell(self):
        """
        Obtain the k-path for a 2*1*1 supercell of a non-standard cubic system.
        """
        import warnings
        from seekpath import SupercellWarning

        cell = [[8.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
        positions = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]
        atomic_numbers = [1, 1]

        s = np.sin(0.3)
        c = np.cos(0.3)
        R = np.array([[-1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]])

        T = np.array([[1, 0, 1], [0, 1, 2], [0, 0, -1]])

        cell = T @ cell @ R
        positions = positions @ np.linalg.inv(T)
        system = (cell, positions, atomic_numbers)

        with warnings.catch_warnings(record=True) as w:
            res = self.base_test(system)
            self.assertEqual(res["is_supercell"], True)

            # Checks on issued warnings
            relevant_w = [_ for _ in w if issubclass(_.category, SupercellWarning)]
            self.assertEqual(
                len(relevant_w),
                1,
                "Wrong number of warnings issued! "
                "({} instead of 1)".format(len(relevant_w)),
            )

            check_string = "The provided cell is a supercell: the returned"
            if check_string is not None:
                self.assertIn(check_string, str(relevant_w[0].message))

        self.assertEqual(res["spacegroup_international"], "Pm-3m")

    def test_no_symmetrization(self):
        """
        Test that symmetrization is not performed so that the k path is on
        a non-high-symmetric points when the cell is slightly distorted below
        the symmetry precision.
        """
        cell = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0 + 1e-6]]
        positions = [[0, 0, 0]]
        atomic_numbers = [0]
        system = (cell, positions, atomic_numbers)

        import seekpath

        res_standard = seekpath.get_path(system)
        res_original = seekpath.get_path_orig_cell(system)

        self.assertEqual(res_standard["spacegroup_international"], "Pm-3m")
        self.assertEqual(res_original["spacegroup_international"], "Pm-3m")

        xk_R = np.array([0.5, 0.5, 0.5])
        np.testing.assert_almost_equal(res_standard["point_coords"]["R"], xk_R)
        self.assertGreater(np.sum(abs(res_original["point_coords"]["R"] - xk_R)), 1e-7)


class TestExplicitPaths_Orig_Cell(unittest.TestCase):
    """Test the creation of explicit paths for the original cell."""

    def test_keys(self):  # pylint: disable=no-self-use
        """
        Test the keys for a non-standard fcc unit cell.
        """
        import seekpath

        cell = [[-3.0, 0.0, 3.0], [0.0, 3.0, 3.0], [-3.0, 3.0, 0.0]]
        positions = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        atomic_numbers = [0, 0]

        system = (cell, positions, atomic_numbers)

        res = seekpath.get_explicit_k_path_orig_cell(system, recipe="hpkot")

        known_keys = set(
            [
                "augmented_path",
                "explicit_kpoints_abs",
                "explicit_kpoints_labels",
                "explicit_kpoints_linearcoord",
                "explicit_kpoints_rel",
                "explicit_segments",
                "is_supercell",
                "path",
                "point_coords",
            ]
        )

        missing_known_keys = known_keys - set(res.keys())
        if missing_known_keys:
            raise AssertionError(
                "Some keys are not returned from the "
                "get_explicit_k_path_orig_cell function: {}".format(
                    ", ".join(missing_known_keys)
                )
            )

    def test_path(self):  # pylint: disable=no-self-use
        """
        Test the explicit k path for a non-standard fcc unit cell by comparing
        them with the k path for the standardized unit cell.
        """
        import seekpath
        import warnings
        from seekpath import SupercellWarning

        cell = [[-3.0, 0.0, 3.0], [0.0, 3.0, 3.0], [-3.0, 3.0, 0.0]]
        positions = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        atomic_numbers = [1, 1]

        s = np.sin(0.3)
        c = np.cos(0.3)
        R = np.array([[-1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]])
        cell = cell @ R

        system = (cell, positions, atomic_numbers)

        res_standard = seekpath.get_explicit_k_path(system, recipe="hpkot")

        with warnings.catch_warnings(record=True) as w:
            res_original = seekpath.get_explicit_k_path_orig_cell(
                system, recipe="hpkot"
            )
            self.assertEqual(res_original["is_supercell"], True)

            # Checks on issued warnings
            relevant_w = [_ for _ in w if issubclass(_.category, SupercellWarning)]
            self.assertEqual(
                len(relevant_w),
                1,
                "Wrong number of warnings issued! "
                "({} instead of 1)".format(len(relevant_w)),
            )

            check_string = "The provided cell is a supercell: the returned"
            if check_string is not None:
                self.assertIn(check_string, str(relevant_w[0].message))

        self.assertEqual(res_original["path"], res_standard["path"])
        self.assertEqual(res_original["augmented_path"], res_standard["augmented_path"])
        self.assertEqual(
            res_original["explicit_kpoints_labels"],
            res_standard["explicit_kpoints_labels"],
        )
        self.assertEqual(
            res_original["explicit_segments"], res_standard["explicit_segments"]
        )
        self.assertEqual(
            res_original["explicit_kpoints_abs"].shape,
            res_standard["explicit_kpoints_abs"].shape,
        )
        self.assertEqual(
            res_original["explicit_kpoints_rel"].shape,
            res_standard["explicit_kpoints_rel"].shape,
        )
        np.testing.assert_array_almost_equal(
            res_original["explicit_kpoints_linearcoord"],
            res_standard["explicit_kpoints_linearcoord"],
        )

        # Test that the k path for the original cell in Cartesian coordinates
        # is identical to that of the standardized cell rotated by the rotation
        # matrix.
        # "explicit_kpoints_abs",
        # "explicit_kpoints_rel",
        reciprocal_original_lattice = np.linalg.inv(system[0]).T * 2 * np.pi
        for ik in range(len(res_original["explicit_kpoints_abs"])):
            k_abs = res_original["explicit_kpoints_abs"][ik]
            k_rel = res_original["explicit_kpoints_rel"][ik]
            k_abs_standard = res_standard["explicit_kpoints_abs"][ik]
            # Test k_abs and k_rel are consistent with the unit cell
            np.testing.assert_array_almost_equal(
                k_abs, k_rel @ reciprocal_original_lattice
            )

            # Test k_abs is identical to that of the standardized cell rotated
            # by the rotation matrix.
            np.testing.assert_array_almost_equal(
                k_abs, k_abs_standard @ res_standard["rotation_matrix"]
            )
