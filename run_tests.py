import unittest
import numpy as np
import seekpath
import seekpath.aiidawrappers

# Import all tests here
from seekpath.test_paths_hpkot import *
from seekpath.hpkot.test_get_primitive import *
from seekpath.brillouinzone.test_brillouinzone import *


def has_aiida():
    try:
        import aiida
        return True
    except ImportError:
        return False


if has_aiida():
    from aiida import load_dbenv
    load_dbenv()
    from aiida.orm.data.structure import Kind, StructureData, Site
from seekpath.aiidawrappers import get_explicit_k_path, get_path


def to_list_of_lists(lofl):
    return [[el for el in l] for l in lofl]


class TestConversion(unittest.TestCase):

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_simple_to_aiida(self):
        cell = np.array([[4., 1., 0.], [0., 4., 0.], [0., 0., 4.]])

        relcoords = np.array([[0.09493671, 0., 0.], [0.59493671, 0.5, 0.5],
                              [0.59493671, 0.5, 0.], [0.59493671, 0., 0.5],
                              [0.09493671, 0.5, 0.5]])

        abscoords = np.dot(cell.T, relcoords.T).T

        numbers = [56, 22, 8, 8, 8]

        struc = seekpath.aiidawrappers._tuple_to_aiida(
            (cell, relcoords, numbers))

        self.assertAlmostEqual(
            np.sum(np.abs(np.array(struc.cell) - np.array(cell))), 0.)
        self.assertAlmostEqual(
            np.sum(
                np.abs(
                    np.array([site.position for site in struc.sites]) -
                    np.array(abscoords))), 0.)
        self.assertEqual([site.kind_name for site in struc.sites],
                         ['Ba', 'Ti', 'O', 'O', 'O'])

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_complex1_to_aiida(self):
        cell = np.array([[4., 1., 0.], [0., 4., 0.], [0., 0., 4.]])

        relcoords = np.array([[0.09493671, 0., 0.], [0.59493671, 0.5, 0.5],
                              [0.59493671, 0.5, 0.], [0.59493671, 0., 0.5],
                              [0.09493671, 0.5, 0.5], [0.09493671, 0.5, 0.5],
                              [0.09493671, 0.5, 0.5], [0.09493671, 0.5, 0.5],
                              [0.09493671, 0.5, 0.5]])

        abscoords = np.dot(cell.T, relcoords.T).T

        numbers = [56, 22, 8, 8, 8, 56000, 200000, 200001, 56001]

        kind_info = {
            'Ba': 56,
            'Ba2': 56000,
            'Ba3': 56001,
            'BaTi': 200000,
            'BaTi2': 200001,
            'O': 8,
            'Ti': 22
        }

        kind_info_wrong = {
            'Ba': 56,
            'Ba2': 56000,
            'Ba3': 56002,
            'BaTi': 200000,
            'BaTi2': 200001,
            'O': 8,
            'Ti': 22
        }

        kinds = [
            Kind(name='Ba', symbols="Ba"),
            Kind(name='Ti', symbols="Ti"),
            Kind(name='O', symbols="O"),
            Kind(name='Ba2', symbols="Ba", mass=100.),
            Kind(name='BaTi',
                 symbols=("Ba", "Ti"),
                 weights=(0.5, 0.5),
                 mass=100.),
            Kind(name='BaTi2',
                 symbols=("Ba", "Ti"),
                 weights=(0.4, 0.6),
                 mass=100.),
            Kind(name='Ba3', symbols="Ba", mass=100.)
        ]

        kinds_wrong = [
            Kind(name='Ba', symbols="Ba"),
            Kind(name='Ti', symbols="Ti"),
            Kind(name='O', symbols="O"),
            Kind(name='Ba2', symbols="Ba", mass=100.),
            Kind(name='BaTi',
                 symbols=("Ba", "Ti"),
                 weights=(0.5, 0.5),
                 mass=100.),
            Kind(name='BaTi2',
                 symbols=("Ba", "Ti"),
                 weights=(0.4, 0.6),
                 mass=100.),
            Kind(name='Ba4', symbols="Ba", mass=100.)
        ]

        # Must specify also kind_info and kinds
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),)

        # There is no kind_info for one of the numbers
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),
                kind_info=kind_info_wrong,
                kinds=kinds)

        # There is no kind in the kinds for one of the labels
        # specified in kind_info
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),
                kind_info=kind_info,
                kinds=kinds_wrong)

        struc = seekpath.aiidawrappers._tuple_to_aiida(
            (cell, relcoords, numbers), kind_info=kind_info, kinds=kinds)

        self.assertAlmostEqual(
            np.sum(np.abs(np.array(struc.cell) - np.array(cell))), 0.)
        self.assertAlmostEqual(
            np.sum(
                np.abs(
                    np.array([site.position for site in struc.sites]) -
                    np.array(abscoords))), 0.)
        self.assertEqual(
            [site.kind_name for site in struc.sites],
            ['Ba', 'Ti', 'O', 'O', 'O', 'Ba2', 'BaTi', 'BaTi2', 'Ba3'])

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_from_aiida(self):
        cell = np.array([[4., 1., 0.], [0., 4., 0.], [0., 0., 4.]])

        struc = StructureData(cell=cell)
        struc.append_atom(symbols='Ba', position=(0, 0, 0))
        struc.append_atom(symbols='Ti', position=(1, 2, 3))
        struc.append_atom(symbols='O', position=(-1, -2, -4))
        struc.append_kind(Kind(name='Ba2', symbols="Ba", mass=100.))
        struc.append_site(Site(kind_name='Ba2', position=[3, 2, 1]))
        struc.append_kind(
            Kind(name='Test',
                 symbols=["Ba", "Ti"],
                 weights=[0.2, 0.4],
                 mass=120.))
        struc.append_site(Site(kind_name='Test', position=[3, 5, 1]))

        struc_tuple, kind_info, kinds = seekpath.aiidawrappers._aiida_to_tuple(
            struc)

        abscoords = np.array([_.position for _ in struc.sites])
        struc_relpos = np.dot(np.linalg.inv(cell.T), abscoords.T).T

        self.assertAlmostEqual(
            np.sum(np.abs(np.array(struc.cell) - np.array(struc_tuple[0]))), 0.)
        self.assertAlmostEqual(
            np.sum(np.abs(np.array(struc_tuple[1]) - struc_relpos)), 0.)

        expected_kind_info = [kind_info[site.kind_name] for site in struc.sites]
        self.assertEqual(struc_tuple[2], expected_kind_info)

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_aiida_roundtrip(self):
        cell = np.array([[4., 1., 0.], [0., 4., 0.], [0., 0., 4.]])

        struc = StructureData(cell=cell)
        struc.append_atom(symbols='Ba', position=(0, 0, 0))
        struc.append_atom(symbols='Ti', position=(1, 2, 3))
        struc.append_atom(symbols='O', position=(-1, -2, -4))
        struc.append_kind(Kind(name='Ba2', symbols="Ba", mass=100.))
        struc.append_site(Site(kind_name='Ba2', position=[3, 2, 1]))
        struc.append_kind(
            Kind(name='Test',
                 symbols=["Ba", "Ti"],
                 weights=[0.2, 0.4],
                 mass=120.))
        struc.append_site(Site(kind_name='Test', position=[3, 5, 1]))

        struc_tuple, kind_info, kinds = seekpath.aiidawrappers._aiida_to_tuple(
            struc)
        roundtrip_struc = seekpath.aiidawrappers._tuple_to_aiida(
            struc_tuple, kind_info, kinds)

        self.assertAlmostEqual(
            np.sum(
                np.abs(np.array(struc.cell) - np.array(roundtrip_struc.cell))),
            0.)
        self.assertEqual(struc.get_attr('kinds'),
                         roundtrip_struc.get_attr('kinds'))
        self.assertEqual([_.kind_name for _ in struc.sites],
                         [_.kind_name for _ in roundtrip_struc.sites])
        self.assertEqual(
            np.sum(
                np.abs(
                    np.array([_.position for _ in struc.sites]) -
                    np.array([_.position for _ in roundtrip_struc.sites]))), 0.)


class TestAiiDAExplicitPath(unittest.TestCase):

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_simple(self):
        import numpy as np
        from aiida.orm import DataFactory
        structure = DataFactory('structure')(
            cell=[[4, 0, 0], [0, 4, 0], [0, 0, 6]])
        structure.append_atom(symbols='Ba', position=[0, 0, 0])
        structure.append_atom(symbols='Ti', position=[2, 2, 3])
        structure.append_atom(symbols='O', position=[2, 2, 0])
        structure.append_atom(symbols='O', position=[2, 0, 3])
        structure.append_atom(symbols='O', position=[0, 2, 3])

        params = DataFactory('parameter')(dict={
            'with_time_reversal': True,
            'reference_distance': 0.025,
            'recipe': 'hpkot',
            'threshold': 1.e-7
        })

        return_value = get_explicit_k_path(structure, params)
        retdict = return_value['seekpath_parameters'].get_dict()

        self.assertTrue(retdict['has_inversion_symmetry'])
        self.assertFalse(retdict['augmented_path'])
        self.assertAlmostEqual(retdict['volume_original_wrt_prim'], 1.0)
        self.assertEqual(to_list_of_lists(retdict['explicit_segments']),
                         [[0, 31], [30, 61], [60, 104], [103, 123], [122, 153],
                          [152, 183], [182, 226], [226, 246], [246, 266]])

        ret_k = return_value['explicit_kpoints']
        self.assertEqual(to_list_of_lists(ret_k.labels),
                         [[0, 'GAMMA'], [30, 'X'], [60, 'M'], [103, 'GAMMA'],
                          [122, 'Z'], [152, 'R'], [182, 'A'], [225, 'Z'],
                          [226, 'X'], [245, 'R'], [246, 'M'], [265, 'A']])
        kpts = ret_k.get_kpoints(cartesian=False)
        highsympoints_relcoords = [kpts[idx] for idx, label in ret_k.labels]
        self.assertAlmostEqual(
            np.sum(
                np.abs(
                    np.array([
                        [0., 0., 0.],  # Gamma
                        [0., 0.5, 0.],  # X
                        [0.5, 0.5, 0.],  # M
                        [0., 0., 0.],  # Gamma
                        [0., 0., 0.5],  # Z
                        [0., 0.5, 0.5],  # R
                        [0.5, 0.5, 0.5],  # A
                        [0., 0., 0.5],  # Z
                        [0., 0.5, 0.],  # X
                        [0., 0.5, 0.5],  # R
                        [0.5, 0.5, 0.],  # M
                        [0.5, 0.5, 0.5],  # A
                    ]) - np.array(highsympoints_relcoords))),
            0.)

        ret_prims = return_value['primitive_structure']
        ret_convs = return_value['conv_structure']
        # The primitive structure should be the same as the one I input
        self.assertAlmostEqual(
            np.sum(np.abs(np.array(structure.cell) - np.array(ret_prims.cell))),
            0.)
        self.assertEqual([_.kind_name for _ in structure.sites],
                         [_.kind_name for _ in ret_prims.sites])
        self.assertEqual(
            np.sum(
                np.abs(
                    np.array([_.position for _ in structure.sites]) -
                    np.array([_.position for _ in ret_prims.sites]))), 0.)

        # Also the conventional structure should be the same as the one I input
        self.assertAlmostEqual(
            np.sum(np.abs(np.array(structure.cell) - np.array(ret_convs.cell))),
            0.)
        self.assertEqual([_.kind_name for _ in structure.sites],
                         [_.kind_name for _ in ret_convs.sites])
        self.assertEqual(
            np.sum(
                np.abs(
                    np.array([_.position for _ in structure.sites]) -
                    np.array([_.position for _ in ret_convs.sites]))), 0.)


class TestAiiDAPath(unittest.TestCase):

    @unittest.skipIf(not has_aiida(), "No AiiDA available")
    def test_simple(self):
        import numpy as np
        from aiida.orm import DataFactory
        structure = DataFactory('structure')(
            cell=[[4, 0, 0], [0, 4, 0], [0, 0, 6]])
        structure.append_atom(symbols='Ba', position=[0, 0, 0])
        structure.append_atom(symbols='Ti', position=[2, 2, 3])
        structure.append_atom(symbols='O', position=[2, 2, 0])
        structure.append_atom(symbols='O', position=[2, 0, 3])
        structure.append_atom(symbols='O', position=[0, 2, 3])

        params = DataFactory('parameter')(dict={
            'with_time_reversal': True,
            'recipe': 'hpkot',
            'threshold': 1.e-7
        })

        return_value = get_path(structure, params)
        retdict = return_value['seekpath_parameters'].get_dict()

        self.assertTrue(retdict['has_inversion_symmetry'])
        self.assertFalse(retdict['augmented_path'])
        self.assertAlmostEqual(retdict['volume_original_wrt_prim'], 1.0)
        self.assertAlmostEqual(retdict['volume_original_wrt_conv'], 1.0)
        self.assertEqual(retdict['bravais_lattice'], 'tP')
        self.assertEqual(retdict['bravais_lattice_extended'], 'tP1')
        self.assertEqual(
            to_list_of_lists(retdict['path']),
            [['GAMMA', 'X'], ['X', 'M'], ['M', 'GAMMA'], ['GAMMA', 'Z'],
             ['Z', 'R'], ['R', 'A'], ['A', 'Z'], ['X', 'R'], ['M', 'A']])

        self.assertEqual(
            retdict['point_coords'], {
                'A': [0.5, 0.5, 0.5],
                'M': [0.5, 0.5, 0.0],
                'R': [0.0, 0.5, 0.5],
                'X': [0.0, 0.5, 0.0],
                'Z': [0.0, 0.0, 0.5],
                'GAMMA': [0.0, 0.0, 0.0]
            })

        self.assertAlmostEqual(
            np.sum(
                np.abs(
                    np.array(retdict['inverse_primitive_transformation_matrix'])
                    - np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))), 0.)

        ret_prims = return_value['primitive_structure']
        ret_convs = return_value['conv_structure']
        # The primitive structure should be the same as the one I input
        self.assertAlmostEqual(
            np.sum(np.abs(np.array(structure.cell) - np.array(ret_prims.cell))),
            0.)
        self.assertEqual([_.kind_name for _ in structure.sites],
                         [_.kind_name for _ in ret_prims.sites])
        self.assertEqual(
            np.sum(
                np.abs(
                    np.array([_.position for _ in structure.sites]) -
                    np.array([_.position for _ in ret_prims.sites]))), 0.)

        # Also the conventional structure should be the same as the one I input
        self.assertAlmostEqual(
            np.sum(np.abs(np.array(structure.cell) - np.array(ret_convs.cell))),
            0.)
        self.assertEqual([_.kind_name for _ in structure.sites],
                         [_.kind_name for _ in ret_convs.sites])
        self.assertEqual(
            np.sum(
                np.abs(
                    np.array([_.position for _ in structure.sites]) -
                    np.array([_.position for _ in ret_convs.sites]))), 0.)


if __name__ == "__main__":
    unittest.main()
