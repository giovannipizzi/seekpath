import unittest

class TestPaths3D_HKOT(unittest.TestCase):
    """
    Class to test the creation of paths for all cases using example structures
    """
    # If True, print on stdout the band paths
    verbose_tests = True

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

        # With time reversal set to False to get the most complete path
        res = hkot.get_path(asecell, with_time_reversal=False) 

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

    def test_oA1Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oA1.
        """
        self.base_test(case="oA1", with_inv = True)        

    def test_oA1N(self):
        """
        Obtain the k-path for a test system without inversion symmetry and
        lattice case oA1.
        """
        self.base_test(case="oA1", with_inv = False)

    def test_oA2Y(self):
        """
        Obtain the k-path for a test system with inversion symmetry and
        lattice case oA2.
        """
        self.base_test(case="oA2", with_inv = True)        

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

## OF2Y does not exist by symmetry
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