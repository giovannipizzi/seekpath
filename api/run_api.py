#!/usr/bin/env python
import flask
app = flask.Flask(__name__)
import tempfile

import sys, os

sys.path.append(os.path.realpath(os.path.join(
    os.path.split(os.path.realpath(__file__))[0], os.pardir)))

import ase, ase.io
import json
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

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
    from ase.data import atomic_numbers

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

    return response

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

        out_json_data = get_json_for_visualizer(in_json_data['cell'], 
            in_json_data['scaled_coords'],
            in_json_data['atomic_numbers'])
        ## 2. get kpath data
        ## 3. visualize it

        raw_code = json.dumps(out_json_data, indent=2)
        ## I manually escape it to then add <br> and pass it to a filter with
        ## |safe. I have to 'unicode' it otherwise it keeps escaping also the
        ## next replaces
        raw_code = unicode(flask.escape(raw_code)).replace(
            '\n', '<br>').replace(' ', '&nbsp;')
        #content = content.replace('\n', '<br>').replace(' ', '&nbsp;')
        #content = "<code>{}</code>".format(content)

        return flask.render_template('visualizer.html', 
                                     jsondata=json.dumps(out_json_data),
                                     raw_code=raw_code)
    else: # GET Request, unexpected
        return flask.redirect('/structure_visualizer')


if __name__ == "__main__":
    app.run(debug=True)
