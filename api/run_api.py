#!/usr/bin/env python
import flask
app = flask.Flask(__name__)
import tempfile

import sys, os
import copy
import numpy as np
import time

sys.path.append(os.path.realpath(os.path.join(
    os.path.split(os.path.realpath(__file__))[0], os.pardir)))

import ase, ase.io, ase.data
from ase.data import chemical_symbols, atomic_numbers
import json
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

time_reversal_note = "The second half of the path is required only if the system does not have time-reversal symmetry"

# From http://arusahni.net/blog/2014/03/flask-nocache.html
from functools import wraps, update_wrapper
import datetime
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view) 

# @app.route("/api/v1/graph/<int:calc_pk>/")
# @nocache
# def return_graph(calc_pk):
#     
#     # To be used, possibly
#     if flask.request.method == 'GET':
#         get_params = flask.request.args
#     else:
#         get_params = {}
# 
#     raw_nodes, raw_links = get_graph(calc_pk)
# 
#     ...
# 
#     return flask.jsonify({"nodes": nodes, "links": links})



# TO IMPROVE FOR SECURITY (EXPOSE ONLY SPECIFIC FILES? MOVE CSS ETC
# UNDER /static? http://flask.pocoo.org/docs/0.10/quickstart/
@app.route('/index.html')
def send_view_index():
    return flask.send_from_directory('view', 'index.html')

@app.route('/')
def index():
    return flask.redirect('/index.html')

@app.route('/structure_visualizer/')
def structure_visualizer():
    return flask.send_from_directory('view', 'structure_visualizer.html')

class UnknownFormatError(ValueError):
    pass

def get_structure_tuple(fileobject, fileformat):
    #with tempfile.NamedTemporaryFile() as f:
    #    structurefile.save(f.name)
    #    print f.name
        
    if fileformat == 'vasp':
        import ase.io.vasp
        asestructure = ase.io.vasp.read_vasp(fileobject)
    else:
        raise UnknownFormatError(fileformat)

    return (
        asestructure.cell.tolist(),
        asestructure.get_scaled_positions().tolist(),
        asestructure.get_chemical_symbols())

def get_atomic_numbers(symbols):
    retlist = []
    for s in symbols:
        try:
            retlist.append(atomic_numbers[s])
        except KeyError:
            raise ValueError("Unknown symbol '{}'".format(s))
    return retlist


def get_json_for_visualizer(cell, relcoords, atomic_numbers):
    import numpy as np
    from kpaths3d import hkot
    from brillouinzone import brillouinzone
    from kpaths3d import get_explicit_k_path

    system = (np.array(cell), np.array(relcoords), np.array(atomic_numbers))
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

    # Response for JS, and path_results
    return response, res

@app.route('/static/js/<path:path>')
def send_js(path):
    print path
    return flask.send_from_directory('static/js', path)

@app.route('/static/css/<path:path>')
def send_css(path):
    print path
    return flask.send_from_directory('static/css', path)


@app.route('/process_structure/', methods=['GET', 'POST'])
def process_structure():
    start_time = time.time()
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'structurefile' not in flask.request.files:
            #flash('No file part')
            return flask.redirect('/structure_visualizer')
        structurefile = flask.request.files['structurefile']
        fileformat = flask.request.form.get('fileformat', 'unknown')
        fileobject = StringIO.StringIO(structurefile.read())

        try:
            structure_tuple = get_structure_tuple(fileobject, fileformat)
        except UnknownFormatError:
            # Return immediately (TODO: change page)
            return flask.render_template(
                'basic_visualizer.html', 
                content="Unknown format '{}'".format(fileformat))
        except Exception:
            return flask.render_template(
                'basic_visualizer.html', 
                content="I tried my best, but I wasn't able to load your "
                    "file in format '{}'...".format(fileformat))

        atomic_numbers = get_atomic_numbers(structure_tuple[2])
        in_json_data = {
            'cell': structure_tuple[0],
            'scaled_coords': structure_tuple[1],
            'symbols': structure_tuple[2],
            'atomic_numbers': atomic_numbers
        }

        out_json_data, path_results = get_json_for_visualizer(
            in_json_data['cell'], 
            in_json_data['scaled_coords'],
            in_json_data['atomic_numbers'])

        raw_code_dict = copy.copy(out_json_data)
        for k in list(raw_code_dict.keys()):
            if k.startswith('explicit_'):
                raw_code_dict.pop(k)
        raw_code_dict.pop('faces_data')
        raw_code_dict['primitive_lattice'] = path_results['primitive_lattice'].tolist()
        raw_code_dict['primitive_positions'] = path_results['primitive_positions'].tolist()
        primitive_positions_cartesian = np.dot(
            np.array(path_results['primitive_positions']),
            np.array(path_results['primitive_lattice']),
            ).tolist()
        primitive_positions_cartesian_refolded = np.dot(
            np.array(path_results['primitive_positions'])%1.,
            np.array(path_results['primitive_lattice']),
            ).tolist()
        raw_code_dict['primitive_positions_cartesian'] = primitive_positions_cartesian

        # raw_code['primitive_types'] = path_results['primitive_types']
        primitive_symbols = [chemical_symbols[num] for num 
            in path_results['primitive_types']]
        raw_code_dict['primitive_symbols'] = primitive_symbols

        raw_code = json.dumps(raw_code_dict, indent=2)
        ## I manually escape it to then add <br> and pass it to a filter with
        ## |safe. I have to 'unicode' it otherwise it keeps escaping also the
        ## next replaces
        raw_code = unicode(flask.escape(raw_code)).replace(
            '\n', '<br>').replace(' ', '&nbsp;')
        #content = content.replace('\n', '<br>').replace(' ', '&nbsp;')
        #content = "<code>{}</code>".format(content)

        kpoints = [[k, out_json_data['kpoints'][k][0], 
            out_json_data['kpoints'][k][1], out_json_data['kpoints'][k][2]] 
            for k in sorted(out_json_data['kpoints'])]

        # print path_results

        direct_vectors = [[idx, coords[0], coords[1], coords[2]]
            for idx, coords in 
            enumerate(path_results['primitive_lattice'], start=1)
        ]

        reciprocal_primitive_vectors = [[idx, coords[0], coords[1], coords[2]]
            for idx, coords in 
            enumerate(path_results['reciprocal_primitive_lattice'], start=1)
        ]

        atoms_scaled = [[label, coords[0], coords[1], coords[2]]
            for label, coords in 
            zip(primitive_symbols, 
                path_results['primitive_positions'])]

        atoms_cartesian = [[label, coords[0], coords[1], coords[2]]
            for label, coords in 
            zip(primitive_symbols, 
                primitive_positions_cartesian)]

        print path_results['path']
        # Create extetically-nice looking path, with dashes and pipes
        suggested_path = []
        if path_results['path']:
            suggested_path.append(path_results['path'][0][0])
            suggested_path.append('-')
            suggested_path.append(path_results['path'][0][1])
            last = path_results['path'][0][1]
        for p1, p2 in path_results['path'][1:]:
            if p1 != last:
                suggested_path.append('|')
                suggested_path.append(p1)
            suggested_path.append('-')
            suggested_path.append(p2)
            last = p2

        primitive_lattice = path_results['primitive_lattice']
        # Manual recenter of the structure
        center = (primitive_lattice[0] + primitive_lattice[1] + primitive_lattice[2])/2.
        cell_json = {
                "t": "UnitCell",
                "i": "s0",
                "o": (-center).tolist(),
                "x": (primitive_lattice[0]-center).tolist(),
                "y": (primitive_lattice[1]-center).tolist(),
                "z": (primitive_lattice[2]-center).tolist(),
                "xy": (primitive_lattice[0] + primitive_lattice[1] - center).tolist(),
                "xz": (primitive_lattice[0] + primitive_lattice[2] - center).tolist(),
                "yz": (primitive_lattice[1] + primitive_lattice[2] - center).tolist(),
                "xyz": (primitive_lattice[0] + primitive_lattice[1] + primitive_lattice[2] - center).tolist(),
            }
        atoms_json = [ 
                    {"l": label,
                    "x": pos[0]-center[0],
                    "y": pos[1]-center[1],
                    "z": pos[2]-center[2]} 
                    for label, pos in zip(primitive_symbols, primitive_positions_cartesian_refolded)
                    ]
        # These will be passed to ChemDoodle
        json_content = {"s": [cell_json], 
                        "m": [{"a": atoms_json}]
                        }
        
        compute_time = time.time() - start_time        
        return flask.render_template(
            'visualizer.html', 
            jsondata=json.dumps(out_json_data),
            json_content=json.dumps(json_content),
            volume_ratio_prim=int(path_results['volume_original_wrt_prim']),
            raw_code=raw_code,
            kpoints=kpoints,
            bravais_lattice=path_results['bravais_lattice'],
            bravais_lattice_case=path_results['bravais_lattice_case'],
            direct_vectors=direct_vectors,
            atoms_scaled=atoms_scaled,
            with_without_time_reversal="with" if path_results['has_inversion_symmetry'] else "without",
            atoms_cartesian=atoms_cartesian,
            reciprocal_primitive_vectors=reciprocal_primitive_vectors,
            suggested_path=suggested_path,
            compute_time=compute_time,
            time_reversal_note=time_reversal_note if path_results['augmented_path'] else ""
            )
    else: # GET Request
        return flask.redirect('/structure_visualizer')


if __name__ == "__main__":
    app.run(debug=True)
