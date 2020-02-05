from __future__ import absolute_import
import unittest


class TestGetPrimitive(unittest.TestCase):
    """
    Test what happens for a supercell
    """

    def test_primitive_bcc(self):
        """
        Test the primitive of a BCC.
        """
        from .spg_mapping import get_primitive
        import numpy as np

        cell = [[4., 0., 0.], [0., 4., 0.], [0., 0., 4.]]
        positions = [[0., 0., 0.], [0.5, 0.5, 0.5], [0., 0.25, 0.],
                     [0.5, 0.75, 0.5]]
        atomic_numbers = [6, 6, 8, 8]

        system = (cell, positions, atomic_numbers)
        prim, PinvP, mapping = get_primitive(system, 'cI')

        self.assertEqual(mapping.tolist(), [0, 0, 1, 1])
        self.assertAlmostEqual(prim[1].tolist(),
                               [[0., 0., 0.], [0.25, 0., 0.25]])

    def test_primitive_oA(self):
        """
        Test the primitive of a oA cell.
        """
        from .spg_mapping import get_primitive
        import numpy as np

        cell = [[9., 0., 0.], [0., 3., 0.], [0., 0., 3.]]
        positions = [[0., 0.5, 0.46903476], [0., 0.5, 0.15103982],
                     [0., 0., 0.65103982], [0.5, 0.5, 0.87367305],
                     [0., 0., 0.96903476], [0.5, 0., 0.37367305]]
        atomic_numbers = [6, 8, 8, 8, 6, 8]

        system = (cell, positions, atomic_numbers)
        prim, PinvP, mapping = get_primitive(system, 'oA')

        self.assertAlmostEqual(prim[0].tolist(),
                               [[0., 1.5, -1.5], [0., 1.5, 1.5], [9., 0., 0.]])
        self.assertEqual(mapping.tolist(), [0, 1, 1, 2, 0, 2])
        self.assertAlmostEqual(
            np.sum(
                np.abs(prim[1] - np.array([[0.03096524, 0.96903476, 0.],
                                           [0.34896018, 0.65103982, 0.],
                                           [-0.37367305, 1.37367305, 0.5]]))),
            0.)

    def test_primitive_oA_with_wrapping(self):
        """
        Test the primitive of a oA cell, wrapping coordinates between 0 and 1.
        """
        from .spg_mapping import get_primitive
        import numpy as np

        cell = [[9., 0., 0.], [0., 3., 0.], [0., 0., 3.]]
        positions = [[0., 0.5, 0.46903476], [0., 0.5, 0.15103982],
                     [0., 0., 0.65103982], [0.5, 0.5, 0.87367305],
                     [0., 0., 0.96903476], [0.5, 0., 0.37367305]]
        atomic_numbers = [6, 8, 8, 8, 6, 8]

        system = (cell, positions, atomic_numbers)
        prim, PinvP, mapping = get_primitive(system,
                                             'oA',
                                             wrap_to_zero_one=True)

        self.assertAlmostEqual(prim[0].tolist(),
                               [[0., 1.5, -1.5], [0., 1.5, 1.5], [9., 0., 0.]])
        self.assertEqual(mapping.tolist(), [0, 1, 1, 2, 0, 2])
        self.assertAlmostEqual(
            np.sum(
                np.abs(prim[1] - np.array([[0.03096524, 0.96903476, 0.],
                                           [0.34896018, 0.65103982, 0.],
                                           [0.62632695, 0.37367305, 0.5]]))),
            0.)
