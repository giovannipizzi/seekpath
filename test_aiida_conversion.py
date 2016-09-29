from aiida import load_dbenv
load_dbenv()

from aiida.orm.data.structure import Kind, StructureData, Site

import unittest
import numpy as np
import seekpath
import seekpath.aiidawrappers

class TestConversion(unittest.TestCase):

    def test_simple_to_aiida(self):
        cell = np.array([[ 4.,  1.,  0.],
                         [ 0.,  4.,  0.],
                         [ 0.,  0.,  4.]])

        relcoords = np.array([
                [ 0.09493671,  0.        ,  0.        ],
                [ 0.59493671,  0.5       ,  0.5       ],
                [ 0.59493671,  0.5       ,  0.        ],
                [ 0.59493671,  0.        ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ]])

        abscoords = np.dot(cell.T, relcoords.T).T

        numbers = [56, 22, 8, 8, 8]

        struc = seekpath.aiidawrappers._tuple_to_aiida(
            (cell, relcoords, numbers))

        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(struc.cell) - np.array(cell))), 0.)
        self.assertAlmostEqual(np.sum(np.abs(
                    np.array([site.position for site in struc.sites]) - np.array(abscoords))), 0.)
        self.assertEqual([site.kind_name for site in struc.sites],
                         ['Ba', 'Ti', 'O', 'O', 'O'])


    def test_complex1_to_aiida(self):
        cell = np.array([[ 4.,  1.,  0.],
                         [ 0.,  4.,  0.],
                         [ 0.,  0.,  4.]])

        relcoords = np.array([
                [ 0.09493671,  0.        ,  0.        ],
                [ 0.59493671,  0.5       ,  0.5       ],
                [ 0.59493671,  0.5       ,  0.        ],
                [ 0.59493671,  0.        ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ],
                [ 0.09493671,  0.5       ,  0.5       ]])

        abscoords = np.dot(cell.T, relcoords.T).T

        numbers = [56, 22, 8, 8, 8, 56000, 200000, 200001, 56001]

        kind_info = {
            'Ba': 56,
            'Ba2': 56000,
            'Ba3': 56001,
            'BaTi': 200000,
            'BaTi2': 200001,
            'O': 8,
            'Ti': 22}

        kind_info_wrong = {
            'Ba': 56,
            'Ba2': 56000,
            'Ba3': 56002,
            'BaTi': 200000,
            'BaTi2': 200001,
            'O': 8,
            'Ti': 22}

        kinds = [
            Kind(name='Ba', symbols="Ba"),
            Kind(name='Ti', symbols="Ti"),
            Kind(name='O', symbols="O"),
            Kind(name='Ba2', symbols="Ba", mass=100.),
            Kind(name='BaTi', symbols=("Ba", "Ti"), weights=(0.5,0.5),
                 mass=100.),
            Kind(name='BaTi2', symbols=("Ba", "Ti"), weights=(0.4,0.6),
                 mass=100.),
            Kind(name='Ba3', symbols="Ba", mass=100.)]

        kinds_wrong = [
            Kind(name='Ba', symbols="Ba"),
            Kind(name='Ti', symbols="Ti"),
            Kind(name='O', symbols="O"),
            Kind(name='Ba2', symbols="Ba", mass=100.),
            Kind(name='BaTi', symbols=("Ba", "Ti"), weights=(0.5,0.5),
                 mass=100.),
            Kind(name='BaTi2', symbols=("Ba", "Ti"), weights=(0.4,0.6),
                 mass=100.),
            Kind(name='Ba4', symbols="Ba", mass=100.)]

        # Must specify also kind_info and kinds
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),
                )

        # There is no kind_info for one of the numbers
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),
                kind_info = kind_info_wrong,
                kinds = kinds
                )

        # There is no kind in the kinds for one of the labels 
        # specified in kind_info
        with self.assertRaises(ValueError):
            struc = seekpath.aiidawrappers._tuple_to_aiida(
                (cell, relcoords, numbers),
                kind_info = kind_info,
                kinds = kinds_wrong
                )

        struc = seekpath.aiidawrappers._tuple_to_aiida(
            (cell, relcoords, numbers),
            kind_info = kind_info,
            kinds = kinds
            )

        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(struc.cell) - np.array(cell))), 0.)
        self.assertAlmostEqual(np.sum(np.abs(
                    np.array([site.position for site in struc.sites]) - np.array(abscoords))), 0.)
        self.assertEqual([site.kind_name for site in struc.sites],
                         ['Ba', 'Ti', 'O', 'O', 'O','Ba2','BaTi','BaTi2','Ba3'])


    def test_from_aiida(self):
        cell = np.array([[ 4.,  1.,  0.],
                         [ 0.,  4.,  0.],
                         [ 0.,  0.,  4.]])
        
        struc = StructureData(cell=cell)
        struc.append_atom(symbols='Ba', position=(0,0,0))
        struc.append_atom(symbols='Ti', position=(1,2,3))
        struc.append_atom(symbols='O', position=(-1,-2,-4))
        struc.append_kind(
            Kind(name='Ba2', symbols="Ba", mass=100.))
        struc.append_site(Site(kind_name='Ba2', position=[3,2,1]))
        struc.append_kind(
            Kind(name='Test', symbols=["Ba", "Ti"],
                 weights=[0.2,0.4], mass=120.))
        struc.append_site(Site(kind_name='Test', position=[3,5,1]))
        
        struc_tuple, kind_info, kinds = seekpath.aiidawrappers._aiida_to_tuple(
            struc
            )
        
        abscoords = np.array([_.position for _ in struc.sites])
        struc_relpos = np.dot(np.linalg.inv(cell.T), abscoords.T).T

        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(struc.cell) - np.array(struc_tuple[0]))), 0.)
        self.assertAlmostEqual(np.sum(np.abs(
                                np.array(struc_tuple[1]) - struc_relpos)), 0.)
        
        expected_kind_info = [kind_info[site.kind_name] for site in struc.sites]
        self.assertEqual(struc_tuple[2], expected_kind_info)
        
    def test_aiida_roundtrip(self):
        cell = np.array([[ 4.,  1.,  0.],
                         [ 0.,  4.,  0.],
                         [ 0.,  0.,  4.]])
        
        struc = StructureData(cell=cell)
        struc.append_atom(symbols='Ba', position=(0,0,0))
        struc.append_atom(symbols='Ti', position=(1,2,3))
        struc.append_atom(symbols='O', position=(-1,-2,-4))
        struc.append_kind(
            Kind(name='Ba2', symbols="Ba", mass=100.))
        struc.append_site(Site(kind_name='Ba2', position=[3,2,1]))
        struc.append_kind(
            Kind(name='Test', symbols=["Ba", "Ti"],
                 weights=[0.2,0.4], mass=120.))
        struc.append_site(Site(kind_name='Test', position=[3,5,1]))
        
        struc_tuple, kind_info, kinds = seekpath.aiidawrappers._aiida_to_tuple(
            struc
            )
        roundtrip_struc = seekpath.aiidawrappers._tuple_to_aiida(
            struc_tuple, kind_info, kinds)

        self.assertAlmostEqual(np.sum(np.abs(
                    np.array(struc.cell) - np.array(roundtrip_struc.cell)
                    )), 0.)
        self.assertEqual(struc.get_attr('kinds'),
                         roundtrip_struc.get_attr('kinds')
                         )
        self.assertEqual([_.kind_name for _ in struc.sites],
                         [_.kind_name for _ in roundtrip_struc.sites])
        self.assertEqual(np.sum(np.abs(
                    np.array([_.position for _ in struc.sites]) - 
                    np.array([_.position for _ in roundtrip_struc.sites]))), 0.)


if __name__ == "__main__":
    unittest.main()
