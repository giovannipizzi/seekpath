from __future__ import absolute_import
from builtins import range
import unittest
import numpy as np

from . import brillouinzone


def has_scipy():
    try:
        import scipy
        return True
    except ImportError:
        return False


def is_same_point(p1, p2):
    threshold = 1.e-7

    l1_dist = np.abs(np.array(p1) - np.array(p2)).sum()
    return l1_dist < threshold


def is_same_face(f1, f2):
    """
    Check if two faces are the same.

    f1 and f2 should be a list of 3d points (i.e., a list of lists).

    It also checks if the the coordinates are shifted (i.e. the first one is 
        now the second, the second the third etc.). Tries also points in 
        reversed order.
    """
    threshold = 1.e-7

    # Must have same # of points
    if len(f1) != len(f2):
        return False

    # Empty faces are the same
    if len(f1) == 0:
        return True

    found = False
    # Find (first occurrence of) first point
    for shift, p2 in enumerate(f2):
        if is_same_point(f1[0], p2):
            found = True
            break

    if not found:
        return False

    # make a new version of f2 with shifted indices, and check
    # now if all points are the same
    indices = (np.arange(len(f2)) + shift) % len(f2)
    err = np.abs(np.array(f1) - np.array(f2)[indices]).mean()
    found = err < threshold
    if found:
        return True
    # Try also reversed order
    indices = (-(np.arange(len(f2)) + shift)) % len(f2)
    err = np.abs(np.array(f1) - np.array(f2)[indices]).mean()
    found = err < threshold
    return found


def are_same_faces(faces1, faces2):
    """
    Return a tuple. The first value is True if the two sets of faces are the 
    same, False otherwise. the second is a string with additional information.
    """
    if len(faces1) != len(faces2):
        return False, ("The two list of faces have different "
                       "length ({} vs. {})".format(len(faces1), len(faces2)))

    remaining_indices = list(range(len(faces1)))
    for f1idx, f1 in enumerate(faces1):
        found = False
        for f2idx in remaining_indices:
            #print '~', f1idx, f2idx
            if is_same_face(f1, faces2[f2idx]):
                #print f1idx, f2idx, remaining_indices
                found = True
                break
        if found:
            remaining_indices.remove(f2idx)
        else:
            # If here, that means that face f1 does not exist in (the
            # remaining faces in) faces2
            return False, ("The following item in the first list was not "
                           "found in the second one: {}".format(f1))
    return True, ""


class TestBZ(unittest.TestCase):
    """
    Test the search for BZ faces
    """

    @unittest.skipIf(not has_scipy(), "No SciPy")
    def test_cubic(self):
        b1 = [1, 0, 0]
        b2 = [0, 1, 0]
        b3 = [0, 0, 1]
        bz = brillouinzone.get_BZ(b1=b1, b2=b2, b3=b3)

        expected_faces = [[[-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5],
                           [0.5, -0.5, 0.5], [0.5, -0.5, -0.5]],
                          [[-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5],
                           [0.5, -0.5, -0.5], [0.5, 0.5, -0.5]],
                          [[-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5],
                           [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5]],
                          [[0.5, -0.5, 0.5], [-0.5, -0.5, 0.5],
                           [-0.5, 0.5, 0.5], [0.5, 0.5, 0.5]],
                          [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5],
                           [0.5, -0.5, 0.5]],
                          [[-0.5, 0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5],
                           [-0.5, 0.5, 0.5]]]

        unexpected_faces_1 = [[[-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5], [0.3, -0.5, -0.5]],
                              [[-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5], [0.5, 0.5, -0.5]],
                              [[-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5],
                               [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5]],
                              [[0.5, -0.5, 0.5], [-0.5, -0.5, 0.5],
                               [-0.5, 0.5, 0.5], [0.5, 0.5, 0.5]],
                              [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                               [0.5, 0.5, 0.5], [0.5, -0.5, 0.5]],
                              [[-0.5, 0.5, -0.5], [0.5, 0.5, -0.5],
                               [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]]]

        # The definition of triangles is not unique. I check directly the
        # faces (that should be obtained from the triangles
        faces = bz['faces']

        #theFaces = [Face(f) for f in faces]
        #theExpectedFaces = [Face(f) for f in expected_faces]
        is_same, info = are_same_faces(faces, expected_faces)
        self.assertTrue(is_same,
                        "The two sets of faces are different: {}".format(info))

        is_same, info = are_same_faces(faces, unexpected_faces_1)
        self.assertFalse(is_same,
                         "The two sets of faces are not detected as different")

    @unittest.skipIf(not has_scipy(), "No SciPy")
    def test_2(self):
        b1 = [1, 0, 0]
        b2 = [0, 1, 0]
        b3 = [0.2, 0.2, 1]
        bz = brillouinzone.get_BZ(b1=b1, b2=b2, b3=b3)

        expected_faces = [
            [
                [-0.5, 0.3, -0.5],
                [-0.5, -0.5, -0.34],
                [0.3, -0.5, -0.5],
                [0.3, 0.3, -0.66],
            ],
            [
                [0.5, -0.3, 0.5],
                [-0.3, -0.3, 0.66],
                [-0.3, 0.5, 0.5],
                [0.5, 0.5, 0.34],
            ],
            [
                [-0.3, 0.5, 0.5],
                [-0.3, -0.3, 0.66],
                [-0.5, -0.3, 0.5],
                [-0.5, 0.5, 0.34],
            ],
            [
                [-0.3, -0.3, 0.66],
                [0.5, -0.3, 0.5],
                [0.5, -0.5, 0.34],
                [-0.3, -0.5, 0.5],
            ],
            [
                [-0.5, 0.3, -0.5],
                [0.3, 0.3, -0.66],
                [0.3, 0.5, -0.5],
                [-0.5, 0.5, -0.34],
            ],
            [
                [-0.5, 0.3, -0.5],
                [-0.5, -0.5, -0.34],
                [-0.5, -0.5, 0.34],
                [-0.5, -0.3, 0.5],
                [-0.5, 0.5, 0.34],
                [-0.5, 0.5, -0.34],
            ],
            [
                [-0.3, -0.3, 0.66],
                [-0.5, -0.3, 0.5],
                [-0.5, -0.5, 0.34],
                [-0.3, -0.5, 0.5],
            ],
            [
                [-0.5, 0.5, -0.34],
                [-0.5, 0.5, 0.34],
                [-0.3, 0.5, 0.5],
                [0.5, 0.5, 0.34],
                [0.5, 0.5, -0.34],
                [0.3, 0.5, -0.5],
            ],
            [
                [0.5, 0.3, -0.5],
                [0.3, 0.3, -0.66],
                [0.3, 0.5, -0.5],
                [0.5, 0.5, -0.34],
            ],
            [
                [-0.3, -0.5, 0.5],
                [0.5, -0.5, 0.34],
                [0.5, -0.5, -0.34],
                [0.3, -0.5, -0.5],
                [-0.5, -0.5, -0.34],
                [-0.5, -0.5, 0.34],
            ],
            [
                [0.5, 0.3, -0.5],
                [0.5, -0.5, -0.34],
                [0.5, -0.5, 0.34],
                [0.5, -0.3, 0.5],
                [0.5, 0.5, 0.34],
                [0.5, 0.5, -0.34],
            ],
            [
                [0.5, 0.3, -0.5],
                [0.5, -0.5, -0.34],
                [0.3, -0.5, -0.5],
                [0.3, 0.3, -0.66],
            ],
        ]

        # The definition of triangles is not unique. I check directly the
        # faces (that should be obtained from the triangles
        faces = bz['faces']

        # To print the actual output
        #print "["
        #for f in faces:
        #    print "    ["
        #    for p in f:
        #        print "        [{}, {}, {}],".format(*p)
        #    print "    ],"
        #print "]"

        #theFaces = [Face(f) for f in faces]
        #theExpectedFaces = [Face(f) for f in expected_faces]
        is_same, info = are_same_faces(faces, expected_faces)
        self.assertTrue(is_same,
                        "The two sets of faces are different: {}".format(info))


if __name__ == "__main__":

    unittest.main()
