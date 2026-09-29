"""Symmetry backends used to standardize a crystal structure.

seekpath needs only a small part of a full symmetry dataset: the conventional
(standardized) cell, the space-group number and international symbol, the
rotation from the input orientation to the standardized one, and the volume
ratio between the input and the conventional cell. This module normalizes what
the supported symmetry libraries return into a single :class:`SymmetryDataset`,
so that everything downstream in :mod:`seekpath.hpkot` stays backend agnostic.

Two backends are supported:

``spglib``
    The default, and a hard dependency of seekpath.

``moyopy``
    An optional backend. moyopy is a Rust reimplementation of spglib and is
    usually faster. It is queried with ``Setting.spglib()``, which selects the
    same Hall-symbol representative that spglib uses.
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

DEFAULT_BACKEND = 'spglib'
MOYOPY_MIN_VERSION = '0.21'


class SymmetryDetectionError(Exception):
    """Error raised if the symmetry of the structure could not be detected."""


@dataclass
class SymmetryDataset:
    """The subset of a symmetry dataset that seekpath uses.

    :param number: the international space-group number.
    :param international: the international (Hermann-Mauguin) symbol, without
        spaces.
    :param std_lattice: the conventional cell, as a 3x3 array with the lattice
        vectors as *rows*.
    :param std_positions: fractional coordinates of the atoms in the
        conventional cell.
    :param std_types: atomic numbers of the atoms in the conventional cell.
    :param std_rotation_matrix: the rotation in Cartesian space bringing the
        input structure onto the standardized one.
    :param volume_original_wrt_conv: the volume of the input cell divided by
        the volume of the conventional cell.
    """

    number: int
    international: str
    std_lattice: np.ndarray
    std_positions: np.ndarray
    std_types: np.ndarray
    std_rotation_matrix: np.ndarray
    volume_original_wrt_conv: float


def get_symmetry_dataset(
    structure, symprec=1e-05, angle_tolerance=-1.0, backend=DEFAULT_BACKEND
):
    """Standardize ``structure`` with the requested backend.

    :param structure: a tuple ``(cell, positions, numbers)``, with the lattice
        vectors as rows of ``cell`` and ``positions`` in fractional
        coordinates.
    :param symprec: the symmetry precision.
    :param angle_tolerance: the angle tolerance. The spglib convention of a
        negative value meaning "use the default" is honoured by both backends.
    :param backend: one of :data:`SUPPORTED_BACKENDS`.

    :return: a :class:`SymmetryDataset`.

    :raise ValueError: if ``backend`` is not a supported backend.
    :raise SymmetryDetectionError: if the backend could not detect the
        symmetry of the structure.
    """
    try:
        get_dataset = _BACKENDS[backend]
    except KeyError:
        raise ValueError(
            f"Unknown symmetry backend '{backend}', should be one of {SUPPORTED_BACKENDS}"
        ) from None
    return get_dataset(structure, symprec, angle_tolerance)


def _get_spglib_dataset(structure, symprec, angle_tolerance):
    """Build a :class:`SymmetryDataset` with spglib."""
    from .tools import check_spglib_version, get_dot_access_dataset

    spglib = check_spglib_version()

    dataset = get_dot_access_dataset(
        spglib.get_symmetry_dataset(
            structure, symprec=symprec, angle_tolerance=angle_tolerance
        )
    )
    if dataset is None:
        raise SymmetryDetectionError(
            'spglib could not detect the symmetry of the system'
        )

    return SymmetryDataset(
        number=dataset.number,
        international=dataset.international,
        std_lattice=np.array(dataset.std_lattice),
        std_positions=np.array(dataset.std_positions),
        std_types=np.array(dataset.std_types),
        std_rotation_matrix=np.array(dataset.std_rotation_matrix),
        volume_original_wrt_conv=np.linalg.det(dataset.transformation_matrix),
    )


def _get_moyopy_dataset(structure, symprec, angle_tolerance):
    """Build a :class:`SymmetryDataset` with moyopy."""
    moyopy = _check_moyopy_version()

    cell, positions, numbers = structure
    moyo_cell = moyopy.Cell(
        np.array(cell, dtype=float).tolist(),
        np.array(positions, dtype=float).tolist(),
        np.array(numbers).tolist(),
    )

    try:
        dataset = moyopy.MoyoDataset(
            moyo_cell,
            symprec=symprec,
            angle_tolerance=(
                np.deg2rad(angle_tolerance) if angle_tolerance > 0 else None
            ),
            setting=moyopy.Setting.spglib(),
        )
    except Exception as exc:
        raise SymmetryDetectionError(
            f'moyopy could not detect the symmetry of the system: {exc}'
        ) from exc

    international = moyopy.SpaceGroupType(dataset.number).hm_short.replace(' ', '')

    volume_original_wrt_conv = 1 / np.linalg.det(np.array(dataset.std_linear))

    return SymmetryDataset(
        number=dataset.number,
        international=international,
        std_lattice=np.array(dataset.std_cell.basis),
        std_positions=np.array(dataset.std_cell.positions),
        std_types=np.array(dataset.std_cell.numbers),
        std_rotation_matrix=np.array(dataset.std_rotation_matrix),
        volume_original_wrt_conv=volume_original_wrt_conv,
    )


@lru_cache(maxsize=None)
def _check_moyopy_version():
    """Import moyopy, checking it is recent enough.

    :return: the moyopy module.

    :raise ValueError: if moyopy is missing or older than
        :data:`MOYOPY_MIN_VERSION`.
    """
    from importlib.metadata import version

    from packaging.version import Version

    try:
        import moyopy
    except ImportError as exc:
        raise ValueError(
            f'moyopy >= {MOYOPY_MIN_VERSION} is required for the '
            "'moyopy' backend, but it could not be imported. Install it "
            'with `pip install seekpath[moyopy]` (requires Python >= 3.10)'
        ) from exc

    if Version(version('moyopy')) < Version(MOYOPY_MIN_VERSION):
        raise ValueError(f'Invalid moyopy version, need >= {MOYOPY_MIN_VERSION}')

    return moyopy


_BACKENDS = {'spglib': _get_spglib_dataset, 'moyopy': _get_moyopy_dataset}
SUPPORTED_BACKENDS = tuple(_BACKENDS)
