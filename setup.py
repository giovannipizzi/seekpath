import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

modulename = 'seekpath'
the_license = "The MIT license"

# Get the version number
folder = os.path.split(os.path.abspath(__file__))[0]
fname = os.path.join(folder, modulename, '__init__.py')
with open(fname) as init:
    ns = {}
    exec (init.read(), ns)
    version = ns['__version__']

setup(
    name=modulename,
    description="A module to obtain and visualize k-vector coefficients and obtain band paths in the Brillouin zone of crystal structures",
    url='http://github.com/giovannipizzi/seekpath',
    license=the_license,
    author = 'Giovanni Pizzi',
    version=version,
    # Abstract dependencies.  Concrete versions are listed in
    # requirements.txt
    # See https://caremad.io/2013/07/setup-vs-requirement/ for an explanation
    # of the difference and
    # http://blog.miguelgrinberg.com/post/the-package-dependency-blues
    # for a useful dicussion
    install_requires=[
        'numpy>=1.0', 'scipy>=0.17', 'spglib>=1.9.4',
    ],
    packages=find_packages(),
    download_url = 'https://github.com/giovannipizzi/seekpath/archive/v{}.tar.gz'.format(version),
    keywords = ['path', 'band structure', 'Brillouin', 'crystallography', 
                'physics', 'primitive cell', 'conventional cell'],
    long_description=open(os.path.join(aiida_folder, 'README.rst')).read(),
)
