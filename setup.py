"""Install the seekpath package."""
import os
import io

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

MODULENAME = "seekpath"

# Get the version number in a dirty way
FOLDER = os.path.split(os.path.abspath(__file__))[0]
FNAME = os.path.join(FOLDER, MODULENAME, "__init__.py")
with open(FNAME) as init:
    # Get lines that match, remove comment part
    # (assuming it's not in the string...)
    VERSIONLINES = [
        l.partition("#")[0] for l in init.readlines() if l.startswith("__version__")
    ]
if len(VERSIONLINES) != 1:
    raise ValueError("Unable to detect the version lines")
VERSIONLINE = VERSIONLINES[0]
VERSION = VERSIONLINE.partition("=")[2].replace('"', "").strip()

setup(
    name=MODULENAME,
    description="A module to obtain and visualize k-vector coefficients and obtain band paths "
    "in the Brillouin zone of crystal structures",
    url="http://github.com/giovannipizzi/seekpath",
    license="The MIT license",
    author="Giovanni Pizzi",
    version=VERSION,
    # Abstract dependencies.  Concrete versions are listed in
    # requirements.txt
    # See https://caremad.io/2013/07/setup-vs-requirement/ for an explanation
    # of the difference and
    # http://blog.miguelgrinberg.com/post/the-package-dependency-blues
    # for a useful dicussion
    install_requires=["numpy>=1.0", "spglib>=1.14.1"],
    extras_require={
        "bz": ["scipy>=1"],
        "dev": [
            "pre-commit==3.3.2",
            "black==23.3.0",
            "prospector==1.2.0",
            "pylint==2.4.4",
            "pytest==7.3.1",
        ],
    },
    python_requires=">=3.5",
    packages=find_packages(),
    # Needed to include some static files declared in MANIFEST.in
    include_package_data=True,
    download_url="https://github.com/giovannipizzi/seekpath/archive/v{}.tar.gz".format(
        VERSION
    ),
    keywords=[
        "path",
        "band structure",
        "Brillouin",
        "crystallography",
        "physics",
        "primitive cell",
        "conventional cell",
    ],
    long_description=io.open(
        os.path.join(FOLDER, "README.rst"), encoding="utf-8"
    ).read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
