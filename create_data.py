#!/usr/bin/env python
import json
import os
import sys

import numpy as np
import ase, ase.io

from brillouinzone import brillouinzone
from kpaths3d import hkot 

try:
    case = sys.argv[1]
    #'cF2'
    with_inv_str = sys.argv[2]
    if with_inv_str == 'inv':
        with_inv = True
    elif with_inv_str == 'noinv':
        with_inv = False
    else:
        raise IndexError
except IndexError:
    print >> sys.stderr, "Usage: {} CASE [inv|noinv], where CASE is e.g. cF1, oF2, ...".format(sys.argv[0])
    sys.exit(1)

# Get the POSCAR with the example structure
this_folder = os.path.split(os.path.abspath(hkot.__file__))[0]
folder = os.path.join(this_folder,"band_path_data",case)
poscar_with_inv = os.path.join(folder,'POSCAR_inversion')
poscar_no_inv = os.path.join(folder,'POSCAR_noinversion')

poscar = poscar_with_inv if with_inv else poscar_no_inv
asecell = ase.io.read(poscar)

system = (asecell.get_cell(), asecell.get_scaled_positions(), 
    asecell.get_atomic_numbers())

res = hkot.get_path(system, with_time_reversal=False) 

real_lattice = res['std_lattice']
rec_lattice = np.linalg.inv(real_lattice).T
b1, b2, b3 = rec_lattice


faces_data = brillouinzone.get_BZ(
    b1 = b1, b2=b2, b3=b3)

response = {}
response['faces_data'] = faces_data
response['b1'] = b1.tolist()
response['b2'] = b2.tolist()
response['b3'] = b3.tolist()
## Convert to absolute
response['kpoints'] = {k: (v[0] * b1 + v[1] * b2 + v[2] * b3).tolist()
    for k,v in res['point_coords'].iteritems()}

invstring = "inv" if with_inv else "noinv"
fname = '{}_{}.json'.format(case, invstring)
with open(fname, 'w') as f:
    json.dump(response,f)

print "{} written.".format(fname)

