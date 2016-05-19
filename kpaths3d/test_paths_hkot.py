import unittest

class TestPaths3D_HKOT_Supercell(unittest.TestCase):
    """
    Test what happens for a supercell
    """
    def test_supercell(self):
        """
        Test a supercell (BCC).
        TODO Implement some real test
        """
        import hkot
        
        cell = [[4.,0.,0.],[0.,10.,0.],[0.,0.,4.]]
        positions = [[0.,0.,0.],[0.5,0.25,0.5],[0.,0.5,0.],[0.5,0.75,0.5]]
        atomic_numbers = [6,6,6,6]

        system = (cell, positions, atomic_numbers)        
        res = hkot.get_path(system, with_time_reversal=False)

        import spglib
        print spglib.standardize_cell(system)
        print res


class TestPaths3D_HKOT_EdgeCases(unittest.TestCase):
    """
    Test the warnings issued for edge cases
    """
    def basic_test(self, cell, positions, atomic_numbers, 
        check_bravais_lattice, check_string=None):
        """
        Given a cell, the positions and the atomic numbers, checks that
        (only one) warning is issued, of type hkot.EdgeCaseWarning,
        that the bravais lattice is the expected one,
        and that (optionally, if specified) the warning message contains
        the given string 'check_string'.

        :param cell: 3x3 list of lattice vectors
        :param positions: Nx3 list of (scaled) positions
        :param atomic_number: list of length N with the atomic numbers
        :check_bravais_lattice: a string with the expected Bravais lattice 
            (e.g., 'tI', 'oF', ...)
        :check_string: if specified, this should be contained in the warning
            message
        """
        import warnings

        import hkot

        system = (cell, positions, atomic_numbers)

        with warnings.catch_warnings(record=True) as w:
            res = hkot.get_path(system, with_time_reversal=False) 
            # Checks
            self.assertEquals(res['bravais_lattice'], check_bravais_lattice)
            self.assertEquals(len(w), 1, 'Wrong number of warnings issued! '
                '({} instead of 1)'.format(len(w)))
            assert issubclass(w[0].category, hkot.EdgeCaseWarning)
            if check_string is not None:
                self.assertIn(check_string, str(w[0].message))

    def test_tI(self):
        """
        Test the edge case for tI.
        """
        cell = [[4.,0.,0.],[0.,4.,0.],[0.,0.,4.]]
        positions = [[0.,0.,0.],[0.5,0.5,0.5],[0.0,0.0,0.1],[0.5,0.5,0.6]]
        atomic_numbers = [6,6,8,8]

        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='tI')

    def test_oF_first(self):
        from math import sqrt

        cell = [[sqrt(1./(1/16. + 1/25.)),0.,0.],[0.,4.,0.],[0.,0.,5.]]
        positions = [[0.,0.,0.],[0.,0.5,0.5],[0.5,0.,0.5],[0.5,0.5,0.]]
        atomic_numbers = [6,6,6,6]
        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='oF', check_string = "but 1/a^2")

    def test_oF_second(self):
        from math import sqrt

        cell = [[10,0,0],[0,21,0],[0,0,sqrt(1./(1/100. + 1/441.))]]
        positions = [
            [0.1729328200000002,  0.5632488700000001,  0.9531259500000002],
            [0.8270671799999998,  0.4367511299999999,  0.9531259500000002],
            [0.0770671799999998,  0.3132488700000001,  0.7031259500000002],
            [0.9229328200000002,  0.6867511299999999,  0.7031259500000002],
            [0.1729328200000002,  0.0632488700000001,  0.4531259500000002],
            [0.8270671799999998,  0.9367511299999998,  0.4531259500000002],
            [0.0770671799999998,  0.8132488700000001,  0.2031259500000002],
            [0.9229328200000002,  0.1867511299999999,  0.2031259500000002],
            [0.6729328200000002,  0.5632488700000001,  0.4531259500000002],
            [0.3270671799999998,  0.4367511299999999,  0.4531259500000002],
            [0.5770671799999998,  0.3132488700000001,  0.2031259500000002],
            [0.4229328200000002,  0.6867511299999999,  0.2031259500000002],
            [0.6729328200000002,  0.0632488700000001,  0.9531259500000002],
            [0.3270671799999998,  0.9367511299999998,  0.9531259500000002],
            [0.5770671799999998,  0.8132488700000001,  0.7031259500000002],
            [0.4229328200000002,  0.1867511299999999,  0.7031259500000002],
            [0.0000000000000000,  0.5000000000000000,  0.4701481000000003],
            [0.7500000000000000,  0.7500000000000000,  0.2201481000000003],
            [0.0000000000000000,  0.0000000000000000,  0.9701481000000002],
            [0.7500000000000000,  0.2500000000000000,  0.7201481000000003],
            [0.5000000000000000,  0.5000000000000000,  0.9701481000000002],
            [0.2500000000000000,  0.7500000000000000,  0.7201481000000003],
            [0.5000000000000000,  0.0000000000000000,  0.4701481000000003],
            [0.2500000000000000,  0.2500000000000000,  0.2201481000000003]]
        atomic_numbers = [6] * 16 + [8] * 8
        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='oF', check_string = "but 1/c^2")

    def test_oI_bc(self):

        cell = [[4.,0.,0.],[0.,5.,0.],[0.,0.,5.]]
        positions = [[0.,0.,0.],[0.5,0.5,0.5], [0.,0.,0.1],[0.5,0.5,0.6]]
        atomic_numbers = [6,6,8,8]
        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='oI', 
            check_string = "but the two longest vectors b and c")

    def test_oC(self):

        cell = [[3.,0.,0.],[0.,3.,0.],[0.,0.,5.]]
        positions = [
            [0.5000000000000000,  0.1136209299999999,  0.7500967299999999],
            [0.5000000000000000,  0.8863790700000000,  0.2500967299999999],
            [0.0000000000000000,  0.6136209300000000,  0.7500967299999999],
            [0.0000000000000000,  0.3863790700000001,  0.2500967299999999],
            [0.0000000000000000,  0.8444605049999999,  0.7659032699999999],
            [0.0000000000000000,  0.1555394950000001,  0.2659032699999999],
            [0.5000000000000000,  0.3444605049999999,  0.7659032699999999],
            [0.5000000000000000,  0.6555394950000001,  0.2659032699999999]]
        atomic_numbers = [6,6,6,6,8,8,8,8]
        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='oC')

    def test_oA(self):

        cell = [[9.,0.,0.],[0.,3.,0.],[0.,0.,3.]]
        positions = [
            [0.0000000000000000,  0.0000000000000000,  0.0309652399999998],
            [0.0000000000000000,  0.5000000000000000,  0.5309652399999998],
            [0.0000000000000000,  0.5000000000000000,  0.8489601849999999],
            [0.5000000000000000,  0.5000000000000000,  0.1263269549999999],
            [0.0000000000000000,  0.0000000000000000,  0.3489601849999999],
            [0.5000000000000000,  0.0000000000000000,  0.6263269549999999]]
        atomic_numbers = [6,6,8,8,8,8]
        self.basic_test(cell, positions, atomic_numbers,
            check_bravais_lattice='oA')

    # For full coverage, we should also implement the tests for the warnings 
    # in the mC cases, and for the oP warnings.


class TestPaths3D_HKOT(unittest.TestCase):
    """
    Class to test the creation of paths for all cases using example structures
    """
    # If True, print on stdout the band paths
    verbose_tests = False

    def base_test(self, case, with_inv):
        """
        Test a specific case, with or without inversion (uses the cell whose
        POSCAR is stored in the directories - they have been obtained by 
        Y. Hinuma from the Materials Project).

        :param case: a string with the Bravais Lattice case (as 'cF1', for 
            instance)
        :param with_inv: if True, consider a system with inversion symmetry,
            otherwise one without (in which case, the get_path function is
            called with the kwarg 'with_time_reversal = False')
        """
        import os
        import ase, ase.io

        import hkot

        # Get the POSCAR with the example structure
        this_folder = os.path.split(os.path.abspath(hkot.__file__))[0]
        folder = os.path.join(this_folder,"band_path_data",case)
        poscar_with_inv = os.path.join(folder,'POSCAR_inversion')
        poscar_no_inv = os.path.join(folder,'POSCAR_noinversion')

        poscar = poscar_with_inv if with_inv else poscar_no_inv
        asecell = ase.io.read(poscar)

        system = (asecell.get_cell(), asecell.get_scaled_positions(), 
            asecell.get_atomic_numbers())

        res = hkot.get_path(system, with_time_reversal=False) 

        self.assertEquals(res['bravais_lattice_case'], case)
        self.assertEquals(res['has_inversion_symmetry'], with_inv)

        if self.verbose_tests:
            print "*** {} (inv={})".format(
                case, with_inv)
            for p1, p2 in res['path']:
                print "   {} -- {}: {} -- {}".format(p1, p2, 
                    res['point_coords'][p1], res['point_coords'][p2])

    def test_aP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case aP2.
        """
        self.base_test(case="aP2", with_inv = True)        

    def test_aP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case aP2.
        """
        self.base_test(case="aP2", with_inv = False)

    def test_aP3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case aP3.
        """
        self.base_test(case="aP3", with_inv = True)        

    def test_aP3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case aP3.
        """
        self.base_test(case="aP3", with_inv = False)

    def test_cF1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case cF1.
        """
        self.base_test(case="cF1", with_inv = True)        

    def test_cF1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case cF1.
        """
        self.base_test(case="cF1", with_inv = False)

    def test_cF2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case cF2.
        """
        self.base_test(case="cF2", with_inv = True)        

    def test_cF2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case cF2.
        """
        self.base_test(case="cF2", with_inv = False)

    def test_cI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case cI1.
        """
        self.base_test(case="cI1", with_inv = True)        

    def test_cI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case cI1.
        """
        self.base_test(case="cI1", with_inv = False)

    def test_cP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case cP1.
        """
        self.base_test(case="cP1", with_inv = True)        

    def test_cP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case cP1.
        """
        self.base_test(case="cP1", with_inv = False)

    def test_cP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case cP2.
        """
        self.base_test(case="cP2", with_inv = True)        

    def test_cP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case cP2.
        """
        self.base_test(case="cP2", with_inv = False)

    def test_hP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case hP1.
        """
        self.base_test(case="hP1", with_inv = True)        

    def test_hP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case hP1.
        """
        self.base_test(case="hP1", with_inv = False)

    def test_hP2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case hP2.
        """
        self.base_test(case="hP2", with_inv = True)        

    def test_hP2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case hP2.
        """
        self.base_test(case="hP2", with_inv = False)

    def test_hR1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case hR1.
        """
        self.base_test(case="hR1", with_inv = True)        

    def test_hR1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case hR1.
        """
        self.base_test(case="hR1", with_inv = False)

    def test_hR2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case hR2.
        """
        self.base_test(case="hR2", with_inv = True)        

    def test_hR2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case hR2.
        """
        self.base_test(case="hR2", with_inv = False)

    def test_mC1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case mC1.
        """
        self.base_test(case="mC1", with_inv = True)        

    def test_mC1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case mC1.
        """
        self.base_test(case="mC1", with_inv = False)

    def test_mC2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case mC2.
        """
        self.base_test(case="mC2", with_inv = True)        

    def test_mC2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case mC2.
        """
        self.base_test(case="mC2", with_inv = False)

    def test_mC3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case mC3.
        """
        self.base_test(case="mC3", with_inv = True)        

    def test_mC3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case mC3.
        """
        self.base_test(case="mC3", with_inv = False)

    def test_mP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case mP1.
        """
        self.base_test(case="mP1", with_inv = True)        

    def test_mP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case mP1.
        """
        self.base_test(case="mP1", with_inv = False)

## oA1Y does not exist by symmetry
#    def test_oA1Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        lattice case oA1.
#        """
#        self.base_test(case="oA1", with_inv = True)        

    def test_oA1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oA1.
        """
        self.base_test(case="oA1", with_inv = False)

## oA2Y does not exist by symmetry
#    def test_oA2Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        lattice case oA2.
#        """
#        self.base_test(case="oA2", with_inv = True)        

    def test_oA2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oA2.
        """
        self.base_test(case="oA2", with_inv = False)

    def test_oC1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oC1.
        """
        self.base_test(case="oC1", with_inv = True)        

    def test_oC1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oC1.
        """
        self.base_test(case="oC1", with_inv = False)

    def test_oC2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oC2.
        """
        self.base_test(case="oC2", with_inv = True)        

    def test_oC2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oC2.
        """
        self.base_test(case="oC2", with_inv = False)

    def test_oF1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oF1.
        """
        self.base_test(case="oF1", with_inv = True)        

    def test_oF1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oF1.
        """
        self.base_test(case="oF1", with_inv = False)

## oF2Y does not exist by symmetry
#    def test_oF2Y(self):
#        """
#        Obtain the k-path for a test system with inversion symmetry and
#        lattice case oF2.
#        """
#        self.base_test(case="oF2", with_inv = True)        

    def test_oF2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oF2.
        """
        self.base_test(case="oF2", with_inv = False)

    def test_oF3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oF3.
        """
        self.base_test(case="oF3", with_inv = True)        

    def test_oF3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oF3.
        """
        self.base_test(case="oF3", with_inv = False)

    def test_oI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oI1.
        """
        self.base_test(case="oI1", with_inv = True)        

    def test_oI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oI1.
        """
        self.base_test(case="oI1", with_inv = False)

    def test_oI2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oI2.
        """
        self.base_test(case="oI2", with_inv = True)        

    def test_oI2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oI2.
        """
        self.base_test(case="oI2", with_inv = False)

    def test_oI3Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oI3.
        """
        self.base_test(case="oI3", with_inv = True)        

    def test_oI3N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oI3.
        """
        self.base_test(case="oI3", with_inv = False)

    def test_oP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oP1.
        """
        self.base_test(case="oP1", with_inv = True)        

    def test_oP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oP1.
        """
        self.base_test(case="oP1", with_inv = False)

    def test_tI1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case tI1.
        """
        self.base_test(case="tI1", with_inv = True)        

    def test_tI1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case tI1.
        """
        self.base_test(case="tI1", with_inv = False)

    def test_tI2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case tI2.
        """
        self.base_test(case="tI2", with_inv = True)        

    def test_tI2N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case tI2.
        """
        self.base_test(case="tI2", with_inv = False)

    def test_tP1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case tP1.
        """
        self.base_test(case="tP1", with_inv = True)        

    def test_tP1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case tP1.
        """
        self.base_test(case="tP1", with_inv = False)


if __name__ == "__main__":
    unittest.main()
