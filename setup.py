import os
import io

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

modulename = 'seekpath'
the_license = "The MIT license"

# Get the version number in a dirty way
folder = os.path.split(os.path.abspath(__file__))[0]
fname = os.path.join(folder, modulename, '__init__.py')
with open(fname) as init:
    ns = {}
    # Get lines that match, remove comment part
    # (assuming it's not in the string...)
    versionlines = [
        l.partition('#')[0]
        for l in init.readlines()
        if l.startswith('__version__')
    ]
if len(versionlines) != 1:
    raise ValueError("Unable to detect the version lines")
versionline = versionlines[0]
version = versionline.partition('=')[2].replace('"', '').strip()

setup(
    name=modulename,
    description=
    "A module to obtain and visualize k-vector coefficients and obtain band paths in the Brillouin zone of crystal structures",
    url='http://github.com/giovannipizzi/seekpath',
    license=the_license,
    author='Giovanni Pizzi',
    version=version,
    # Abstract dependencies.  Concrete versions are listed in
    # requirements.txt
    # See https://caremad.io/2013/07/setup-vs-requirement/ for an explanation
    # of the difference and
    # http://blog.miguelgrinberg.com/post/the-package-dependency-blues
    # for a useful dicussion
    install_requires=[
        'numpy>=1.0',
        'spglib>=1.14.1',
        'future>=0.15',
    ],
    extras_require={
        "bz": ["scipy>=0.17"],
        "webservice": [
            "Flask>=0.12.3",
            "ase>=3.15.0,<3.18; python_version<'3.0'",
            "ase>=3.18.0; python_version>='3.0'",
            "qe-tools>=1.1.1",
            "pymatgen>=2017.7,<2019.1; python_version<'3.0'",
            "monty<=2.0.4; python_version<'3.0'",
            "pymatgen>=2017.7; python_version>='3.0'",
        ],
        "dev": [
            'pre-commit>=1.4', 'yapf==0.29.0', 'prospector>=0.12.7',
            'pylint>=1.8'
        ],
        "click": ['click>=6']
    },
    packages=find_packages(),
    # Needed to include some static files declared in MANIFEST.in
    include_package_data=True,
    download_url='https://github.com/giovannipizzi/seekpath/archive/v{}.tar.gz'.
    format(version),
    keywords=[
        'path', 'band structure', 'Brillouin', 'crystallography', 'physics',
        'primitive cell', 'conventional cell'
    ],
    long_description=io.open(os.path.join(folder, 'README.rst'),
                             encoding="utf-8").read(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
