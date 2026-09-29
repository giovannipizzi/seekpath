"""Test the symmetry backends, and that they agree with each other.

The ``moyopy`` backend is optional, so every test that needs it is skipped when
it is not installed.
"""

import glob
import os

import numpy as np
import pytest
from test_paths_hpkot import simple_read_poscar

import seekpath
from seekpath import hpkot
from seekpath.hpkot.backends import (
    DEFAULT_BACKEND,
    SymmetryDetectionError,
    get_symmetry_dataset,
)

BAND_PATH_DATA = os.path.join(os.path.dirname(hpkot.__file__), 'band_path_data')

try:
    import moyopy as _moyopy  # noqa: F401

    HAS_MOYOPY = True
except ImportError:
    HAS_MOYOPY = False

needs_moyopy = pytest.mark.skipif(not HAS_MOYOPY, reason='moyopy is not installed')

REFERENCE_STRUCTURES = sorted(
    (os.path.basename(folder), os.path.basename(poscar).replace('POSCAR_', ''))
    for folder in glob.glob(os.path.join(BAND_PATH_DATA, '*'))
    if os.path.isdir(folder)
    for poscar in glob.glob(os.path.join(folder, 'POSCAR_*'))
)


def read_reference(ext_bravais, variant):
    """Read the reference POSCAR for an extended Bravais symbol."""
    return simple_read_poscar(
        os.path.join(BAND_PATH_DATA, ext_bravais, f'POSCAR_{variant}')
    )


def ids(param):
    """Readable test ids for the (ext_bravais, variant) pairs."""
    return f'{param[0]}-{param[1]}'


class TestBackendSelection:
    """Test how the backend is selected and validated."""

    def test_default_is_spglib(self):
        """The default backend must stay spglib, for backwards compatibility."""
        assert DEFAULT_BACKEND == 'spglib'

    def test_unknown_backend_raises(self):
        """An unknown backend name is rejected with a helpful message."""
        structure = read_reference('cP1', 'inversion')
        with pytest.raises(ValueError, match="Unknown symmetry backend 'nope'"):
            hpkot.get_path(structure, backend='nope')

    @pytest.mark.parametrize(
        'backend', ['spglib', pytest.param('moyopy', marks=needs_moyopy)]
    )
    def test_symmetry_detection_error(self, backend):
        """Both backends report a failed detection the same way.

        A degenerate cell (two parallel lattice vectors, so zero volume) cannot
        be analysed, and must raise ``SymmetryDetectionError`` whichever backend
        is used, rather than the backend's own exception type.
        """
        degenerate = (
            [[4.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 0.0, 4.0]],
            [[0.0, 0.0, 0.0]],
            [6],
        )
        with pytest.raises(SymmetryDetectionError):
            get_symmetry_dataset(degenerate, backend=backend)


@needs_moyopy
class TestMoyopyDataset:
    """Test the moyopy dataset against the spglib one, field by field."""

    @pytest.mark.parametrize('case', REFERENCE_STRUCTURES, ids=ids)
    def test_dataset_fields_agree(self, case):
        """The standardized cell, space group and volume ratio must agree.

        The atom positions are deliberately not compared: moyo may pick a
        different, symmetry-equivalent origin, which is a legitimate choice and
        does not affect the k-path.
        """
        structure = read_reference(*case)
        spglib_ds = get_symmetry_dataset(structure, backend='spglib')
        moyopy_ds = get_symmetry_dataset(structure, backend='moyopy')

        assert spglib_ds.number == moyopy_ds.number
        assert spglib_ds.international == moyopy_ds.international
        assert sorted(spglib_ds.std_types) == sorted(moyopy_ds.std_types)
        np.testing.assert_allclose(
            spglib_ds.std_lattice, moyopy_ds.std_lattice, atol=1e-8
        )
        np.testing.assert_allclose(
            spglib_ds.volume_original_wrt_conv,
            moyopy_ds.volume_original_wrt_conv,
            atol=1e-8,
        )

    @pytest.mark.parametrize(('degrees', 'expected'), [(-1.0, None), (5.0, 0.0872665)])
    def test_angle_tolerance_is_converted(self, monkeypatch, degrees, expected):
        """seekpath's angle tolerance is in degrees (as spglib's), moyopy's in radians."""
        import moyopy

        received = {}
        original = moyopy.MoyoDataset

        def spy(*args, **kwargs):
            received.update(kwargs)
            return original(*args, **kwargs)

        monkeypatch.setattr(moyopy, 'MoyoDataset', spy)
        get_symmetry_dataset(
            read_reference('cP1', 'inversion'),
            angle_tolerance=degrees,
            backend='moyopy',
        )
        if expected is None:
            assert received['angle_tolerance'] is None
        else:
            assert received['angle_tolerance'] == pytest.approx(expected)


@needs_moyopy
class TestBackendsAgree:
    """Test that both backends give the same k-path for the reference set."""

    @pytest.mark.parametrize('with_time_reversal', [True, False])
    @pytest.mark.parametrize('case', REFERENCE_STRUCTURES, ids=ids)
    def test_get_path_agrees(self, case, with_time_reversal):
        """``get_path`` must give identical results with either backend."""
        structure = read_reference(*case)
        kwargs = {'with_time_reversal': with_time_reversal}
        res_spglib = hpkot.get_path(structure, backend='spglib', **kwargs)
        res_moyopy = hpkot.get_path(structure, backend='moyopy', **kwargs)

        for key in (
            'bravais_lattice',
            'bravais_lattice_extended',
            'spacegroup_number',
            'spacegroup_international',
            'has_inversion_symmetry',
            'augmented_path',
            'path',
        ):
            assert res_spglib[key] == res_moyopy[key], f'{key} differs'

        assert set(res_spglib['point_coords']) == set(res_moyopy['point_coords'])
        for label, coords in res_spglib['point_coords'].items():
            np.testing.assert_allclose(
                coords, res_moyopy['point_coords'][label], atol=1e-6, err_msg=label
            )

        for key in ('primitive_lattice', 'reciprocal_primitive_lattice'):
            np.testing.assert_allclose(
                res_spglib[key], res_moyopy[key], atol=1e-8, err_msg=key
            )

    @pytest.mark.parametrize('case', REFERENCE_STRUCTURES, ids=ids)
    def test_reference_classification(self, case):
        """moyopy must reproduce the HPKOT extended Bravais classification.

        This is the same assertion the spglib-only tests make, so it checks
        moyopy against the reference data rather than only against spglib.
        """
        ext_bravais, variant = case
        structure = read_reference(ext_bravais, variant)
        res = hpkot.get_path(structure, with_time_reversal=False, backend='moyopy')

        assert res['bravais_lattice_extended'] == ext_bravais
        assert res['has_inversion_symmetry'] == variant.startswith('inversion')

    @pytest.mark.parametrize('case', REFERENCE_STRUCTURES, ids=ids)
    def test_explicit_k_path_agrees(self, case):
        """The explicit (interpolated) k-point list must agree as well."""
        structure = read_reference(*case)
        res_spglib = seekpath.get_explicit_k_path(structure, backend='spglib')
        res_moyopy = seekpath.get_explicit_k_path(structure, backend='moyopy')

        assert (
            res_spglib['explicit_kpoints_labels']
            == res_moyopy['explicit_kpoints_labels']
        )
        np.testing.assert_allclose(
            res_spglib['explicit_kpoints_rel'],
            res_moyopy['explicit_kpoints_rel'],
            atol=1e-6,
        )


@needs_moyopy
class TestOrigCellPathsAreEquivalent:
    """Test the k-path expressed in the basis of the *original* cell.

    Unlike ``get_path``, ``get_path_orig_cell`` depends on
    ``std_rotation_matrix``, i.e. on which of the symmetry-equivalent
    standardizations the backend picked. spglib and moyopy may pick different
    ones, so the two paths need not be numerically identical - but they must be
    related by a single symmetry operation of the crystal, which makes them
    physically equivalent.
    """

    @staticmethod
    def _symmetry_equivalent(points_a, points_b, rotations):
        """Is there one operation mapping every k-point of a onto b?"""
        labels = sorted(points_a)
        k_a = np.array([points_a[label] for label in labels])
        k_b = np.array([points_b[label] for label in labels])

        candidates = [np.array(rot, dtype=float) for rot in rotations]
        # Time reversal (k -> -k) is a symmetry of the band structure too
        candidates += [-candidate for candidate in candidates]

        for candidate in candidates:
            for matrix in (candidate, candidate.T):
                difference = k_a @ matrix - k_b
                # Two k-points differing by a reciprocal lattice vector are equal
                difference -= np.round(difference)
                if np.abs(difference).max() < 1e-5:
                    return True
        return False

    @pytest.mark.parametrize('case', REFERENCE_STRUCTURES, ids=ids)
    def test_orig_cell_path_equivalent(self, case):
        """The original-cell k-points must be symmetry-equivalent."""
        import spglib

        structure = read_reference(*case)
        res_spglib = seekpath.get_path_orig_cell(structure, backend='spglib')
        res_moyopy = seekpath.get_path_orig_cell(structure, backend='moyopy')

        assert res_spglib['path'] == res_moyopy['path']

        rotations = spglib.get_symmetry_dataset(structure, symprec=1e-5).rotations
        assert self._symmetry_equivalent(
            res_spglib['point_coords'], res_moyopy['point_coords'], rotations
        )
