#!/usr/bin/env python
import json
import os
import sys

import numpy as np
import ase, ase.io

from brillouinzone import brillouinzone
from kpaths3d import hkot, get_explicit_k_path

# If True, does not expect a case from command line, but generates
# all the available ones
do_them_all = True

def get_json_for_visualizer(case, with_inv):
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

    real_lattice = res['primitive_lattice']
    #rec_lattice = np.linalg.inv(real_lattice).T # Missing 2pi!
    rec_lattice = np.array(hkot.tools.get_reciprocal_cell_rows(real_lattice))
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
    response['path'] = res['path']

    # It should use the same logic, so give the same cell as above
    res_explicit = get_explicit_k_path(system, with_time_reversal=False) 
    for k in ['kpoints_rel', 'kpoints_linearcoord', 'kpoints_labels', 
            'kpoints_abs', 'segments']:
        new_k = "explicit_{}".format(k)
        if isinstance(res_explicit[k], np.ndarray):
            response[new_k] = res_explicit[k].tolist()
        else:
            response[new_k] = res_explicit[k]

    if np.sum(np.abs(np.array(res_explicit['reciprocal_primitive_lattice']) - 
        np.array(res['reciprocal_primitive_lattice']))) > 1.e-7:
        raise AssertionError("Got different reciprocal cells...")

    return response

def write_file(case, with_inv, response):
    invstring = "inv" if with_inv else "noinv"
    fname = 'visualizer/data/{}_{}.json'.format(case, invstring)
    with open(fname, 'w') as f:
        json.dump(response,f)

    print "{} written.".format(fname)


if __name__ == "__main__":
    if do_them_all:
        this_folder = os.path.split(os.path.abspath(hkot.__file__))[0]
        parent_folder =os.path.join(this_folder,"band_path_data")
        for case in os.listdir(parent_folder):
            #if case.startswith('aP'):
            #    print >> sys.stderr, "Warning: skipping aP cases!"
            #    continue
            poscar_with_inv = os.path.join(
                parent_folder,case,'POSCAR_inversion')
            poscar_no_inv = os.path.join(
                parent_folder,case,'POSCAR_noinversion')

            if os.path.exists(poscar_with_inv):
                with_inv = True
                response = get_json_for_visualizer(case, with_inv)
                write_file(case, with_inv, response)
            if os.path.exists(poscar_no_inv):
                with_inv = False
                response = get_json_for_visualizer(case, with_inv)
                write_file(case, with_inv, response)
    else:
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

        response = get_json_for_visualizer(case, with_inv)
        write_file(case, with_inv, response)


