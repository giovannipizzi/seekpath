from aiida import load_dbenv
load_dbenv()

import unittest
from kpaths3d.aiidawrappers import get_explicit_k_path, get_path

class TestAiiDAExplicitPath(unittest.TestCase):
    def test_simple(self):
        import numpy as np
        from aiida.orm import DataFactory
        s = DataFactory('structure')(cell=[
                [4,0,0],
                [0,4,0],
                [0,0,6]])
        s.append_atom(symbols='Ba', position=[0,0,0])
        s.append_atom(symbols='Ti', position=[2,2,3])
        s.append_atom(symbols='O', position=[2,2,0])
        s.append_atom(symbols='O', position=[2,0,3])
        s.append_atom(symbols='O', position=[0,2,3])
        
        retdict = get_explicit_k_path(s, with_time_reversal=True,
                                      reference_distance=0.025,
                                      recipe='hkot', threshold=1.e-7)

        self.assertTrue(retdict['has_inversion_symmetry'])
        self.assertFalse(retdict['augmented_path'])
        self.assertAlmostEqual(retdict['volume_original_wrt_prim'], 1.0)
        self.assertEquals(
            retdict['segments'], 
            [(0, 31), (30, 61), (60, 104), (103, 123), (122, 153), (152, 183),
             (182, 226), (226, 246), (246, 266)])
        ret_s = retdict['primitive_structure']
        ret_k = retdict['explicit_kpoints']
        self.assertEquals(
            ret_k.labels,
            [(0, 'GAMMA'), (30, 'X'), (60, 'M'), (103, 'GAMMA'), (122, 'Z'), 
             (152, 'R'), (182, 'A'), (225, 'Z'), (226, 'X'), (245, 'R'), 
             (246, 'M'), (265, 'A')])
        kpts = ret_k.get_kpoints(cartesian=False)
        highsympoints_relcoords = [kpts[idx] for idx, label in ret_k.labels]
        self.assertAlmostEquals(np.sum(np.abs(
                    np.array([
                            [ 0.,   0.,   0. ], # Gamma
                            [ 0.,   0.5,  0. ], # X
                            [ 0.5,  0.5,  0. ], # M
                            [ 0.,   0.,   0. ], # Gamma
                            [ 0.,   0.,   0.5], # Z
                            [ 0.,   0.5,  0.5], # R
                            [ 0.5,  0.5,  0.5], # A
                            [ 0.,   0.,   0.5], # Z
                            [ 0.,   0.5,  0. ], # X
                            [ 0.,   0.5,  0.5], # R
                            [ 0.5,  0.5,  0. ], # M
                            [ 0.5,  0.5,  0.5], # A
                            ]) -
                    np.array(highsympoints_relcoords))), 0.)
                             
        # The primitive structure should be the same as the one I input
        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(s.cell) - np.array(ret_s.cell)
                    )), 0.)
        self.assertEqual([_.kind_name for _ in s.sites],
                         [_.kind_name for _ in ret_s.sites])
        self.assertEqual(np.sum(np.abs(
                    np.array([_.position for _ in s.sites]) - 
                    np.array([_.position for _ in ret_s.sites]))), 0.)


class TestAiiDAPath(unittest.TestCase):
    def test_simple(self):
        import numpy as np
        from aiida.orm import DataFactory
        s = DataFactory('structure')(cell=[
                [4,0,0],
                [0,4,0],
                [0,0,6]])
        s.append_atom(symbols='Ba', position=[0,0,0])
        s.append_atom(symbols='Ti', position=[2,2,3])
        s.append_atom(symbols='O', position=[2,2,0])
        s.append_atom(symbols='O', position=[2,0,3])
        s.append_atom(symbols='O', position=[0,2,3])
        
        retdict = get_path(s, with_time_reversal=True,
                                      reference_distance=0.025,
                                      recipe='hkot', threshold=1.e-7)

        self.assertTrue(retdict['has_inversion_symmetry'])
        self.assertFalse(retdict['augmented_path'])
        self.assertAlmostEqual(retdict['volume_original_wrt_prim'], 1.0)
        self.assertAlmostEqual(retdict['volume_original_wrt_std'], 1.0)
        self.assertEqual(retdict['bravais_lattice'], 'tP')
        self.assertEqual(retdict['bravais_lattice_case'], 'tP1')
        self.assertEqual(
            retdict['path'], 
            [('GAMMA', 'X'), ('X', 'M'), ('M', 'GAMMA'), ('GAMMA', 'Z'), 
             ('Z', 'R'), ('R', 'A'), ('A', 'Z'), ('X', 'R'), ('M', 'A')])

        self.assertEqual(retdict['point_coords'], {
                'A': [0.5, 0.5, 0.5], 
                'M': [0.5, 0.5, 0.0], 
                'R': [0.0, 0.5, 0.5], 
                'X': [0.0, 0.5, 0.0], 
                'Z': [0.0, 0.0, 0.5], 
                'GAMMA': [0.0, 0.0, 0.0]
                })

        self.assertAlmostEqual(np.sum(np.abs(
            np.array(retdict['inverse_primitive_transformation_matrix'])-
            np.array([[1, 0, 0],
                   [0, 1, 0],
                   [0, 0, 1]]))), 0.)

        ret_prims = retdict['primitive_structure']
        ret_stds = retdict['std_structure']
        # The primitive structure should be the same as the one I input
        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(s.cell) - np.array(ret_prims.cell)
                    )), 0.)
        self.assertEqual([_.kind_name for _ in s.sites],
                         [_.kind_name for _ in ret_prims.sites])
        self.assertEqual(np.sum(np.abs(
                    np.array([_.position for _ in s.sites]) - 
                    np.array([_.position for _ in ret_prims.sites]))), 0.)

        # Also the conventional structure should be the same as the one I input
        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(s.cell) - np.array(ret_stds.cell)
                    )), 0.)
        self.assertEqual([_.kind_name for _ in s.sites],
                         [_.kind_name for _ in ret_stds.sites])
        self.assertEqual(np.sum(np.abs(
                    np.array([_.position for _ in s.sites]) - 
                    np.array([_.position for _ in ret_stds.sites]))), 0.)


if __name__ == "__main__":
    unittest.main()

