#!/usr/bin/env python
"""
Main Flask python function that manages the server backend

If you just want to try it out, just run this file and connect to
http://localhost:5000 from a browser. Otherwise, read the instructions
in README_DEPLOY.md to deploy on a Apache server.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import zip
import flask
import os

import copy
import numpy as np
import time, datetime

import logging, logging.handlers
logger = logging.getLogger("seekpath_server")

logHandler = logging.handlers.RotatingFileHandler(
    os.path.join(
        os.path.split(os.path.realpath(__file__))[0],
        'requests.log'), maxBytes=1000000, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s') 
logHandler.setFormatter(formatter) 
logger.addHandler(logHandler) 
logger.setLevel(logging.DEBUG) 

from ase.data import chemical_symbols
import json
import io

if __name__ == "__main__":
    # If run manually (=> debug/development mode),
    # use the local version of seekpath, not the installed one
    import sys
    sys.path.insert(0, os.path.join(
        os.path.split(__file__)[0], os.pardir))

import seekpath, seekpath.hpkot
from seekpath.brillouinzone import brillouinzone
import spglib # Mainly to get its version

MAX_NUMBER_OF_ATOMS = 256
time_reversal_note = ("The second half of the path is required only if "
                      "the system does not have time-reversal symmetry")

valid_examples = {
    "aP2_inv": ("aP2", True),
    "aP3_inv": ("aP3", True),
    "cF1_inv": ("cF1", True),
    "cF2_inv": ("cF2", True),
    "cI1_inv": ("cI1", True),
    "cP1_inv": ("cP1", True),
    "cP2_inv": ("cP2", True),
    "hP1_inv": ("hP1", True),
    "hP2_inv": ("hP2", True),
    "hR1_inv": ("hR1", True),
    "hR2_inv": ("hR2", True),
    "mC1_inv": ("mC1", True),
    "mC2_inv": ("mC2", True),
    "mC3_inv": ("mC3", True),
    "mP1_inv": ("mP1", True),
    "oC1_inv": ("oC1", True),
    "oC2_inv": ("oC2", True),
    "oF1_inv": ("oF1", True),
    "oF3_inv": ("oF3", True),
    "oI1_inv": ("oI1", True),
    "oI2_inv": ("oI2", True),
    "oI3_inv": ("oI3", True),
    "oP1_inv": ("oP1", True),
    "tI1_inv": ("tI1", True),
    "tI2_inv": ("tI2", True),
    "tP1_inv": ("tP1", True),
    "aP2_noinv": ("aP2", False),
    "aP3_noinv": ("aP3", False),
    "cF1_noinv": ("cF1", False),
    "cF2_noinv": ("cF2", False),
    "cI1_noinv": ("cI1", False),
    "cP1_noinv": ("cP1", False),
    "cP2_noinv": ("cP2", False),
    "hP1_noinv": ("hP1", False),
    "hP2_noinv": ("hP2", False),
    "hR1_noinv": ("hR1", False),
    "hR2_noinv": ("hR2", False),
    "mC1_noinv": ("mC1", False),
    "mC2_noinv": ("mC2", False),
    "mC3_noinv": ("mC3", False),
    "mP1_noinv": ("mP1", False),
    "oA1_noinv": ("oA1", False),
    "oA2_noinv": ("oA2", False),
    "oC1_noinv": ("oC1", False),
    "oC2_noinv": ("oC2", False),
    "oF1_noinv": ("oF1", False),
    "oF2_noinv": ("oF2", False),
    "oF3_noinv": ("oF3", False),
    "oI1_noinv": ("oI1", False),
    "oI2_noinv": ("oI2", False),
    "oI3_noinv": ("oI3", False),
    "oP1_noinv": ("oP1", False),
    "tI1_noinv": ("tI1", False),
    "tI2_noinv": ("tI2", False),
    "tP1_noinv": ("tP1", False),
}

class ConfigurationError(Exception):
    pass

static_folder = os.path.join(os.path.split(os.path.realpath(__file__))[0],
        'static')
view_folder = os.path.join(os.path.split(os.path.realpath(__file__))[0],
        'view')
app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile=True
directory = os.path.split(os.path.realpath(__file__))[0]
try:
    with open(os.path.join(
        directory,
        'SECRET_KEY')) as f:
        app.secret_key = f.readlines()[0].strip()
        if len(app.secret_key) < 16:
            raise ValueError
except Exception:
    raise ConfigurationError(
        "Please create a SECRET_KEY file in {} with a random string "
        "of at least 16 characters".format(directory))

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    Inspired by  http://flask.pocoo.org/snippets/35/

    In apache: use the following reverse proxy (adapt where needed)
    <Location /proxied>
      ProxyPass http://localhost:4444/
      ProxyPassReverse http://localhost:4444/
      RequestHeader set X-Script-Name /proxied
      RequestHeader set X-Scheme http
    </Location>

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_HOST', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)

logger.debug("Start")

# From http://arusahni.net/blog/2014/03/flask-nocache.html
## Add @nocache right between @app.route and the 'def' line
from functools import wraps, update_wrapper
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

def logme(filecontent, fileformat, request, call_source, reason, extra={}):
    """
    Given a string with the file content, a file format, a Flask request and 
    a string identifying the reason for logging, stores the 
    correct logs.

    :param filecontent: a string with the file content
    :param fileformat: string with the file format
    :param request: a Flask request
    :param call_source: a string identifying who called the function
    :param reason: a string identifying the reason for this log
    :param extra: additional data to add to the logged dictionary. 
        NOTE! it must be JSON-serializable
    """
    # I don't know the fileformat
    data = {'filecontent': filecontent, 'fileformat': fileformat}
    
    logdict =  {
        'data': data, 'reason': reason,
        'request': str(request.headers),
        'call_source': call_source,
        'source': request.headers.get(
            'X-Forwarded-For', request.remote_addr),
        'time': datetime.datetime.now().isoformat()
        }
    logdict.update(extra)
    logger.debug(json.dumps(logdict))

def get_json_for_visualizer(cell, relcoords, atomic_numbers):
    system = (np.array(cell), np.array(relcoords), np.array(atomic_numbers))
    res = seekpath.hpkot.get_path(system, with_time_reversal=False) 

    real_lattice = res['primitive_lattice']
    #rec_lattice = np.linalg.inv(real_lattice).T # Missing 2pi!
    rec_lattice = np.array(
        seekpath.hpkot.tools.get_reciprocal_cell_rows(real_lattice))
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
        for k,v in res['point_coords'].items()}
    response['kpoints_rel'] = {k: [v[0], v[1], v[2]]
        for k,v in res['point_coords'].items()}
    response['path'] = res['path']

    # It should use the same logic, so give the same cell as above
    res_explicit = seekpath.get_explicit_k_path(
        system, with_time_reversal=False) 
    for k in res_explicit:
        if k == 'segments' or k.startswith('explicit_'):
            if isinstance(res_explicit[k], np.ndarray):
                response[k] = res_explicit[k].tolist()
            else:
                response[k] = res_explicit[k]

    if np.sum(np.abs(np.array(res_explicit['reciprocal_primitive_lattice']) - 
        np.array(res['reciprocal_primitive_lattice']))) > 1.e-7:
        raise AssertionError("Got different reciprocal cells...")

    # Response for JS, and path_results
    return response, res

def process_structure_core(filecontent, fileformat, call_source=""):
    """
    The main function that generates the data to be sent back to the view.
    
    :param filecontent: The file content (string)
    :param fileformat: The file format (string), among the accepted formats
    :param call_source: a string identifying the source (i.e., who called
       this function). This is a string, mainly for logging reasons.

    :return: this function calls directly flask methods and returns flask 
        objects
    """
    from structure_importers import get_structure_tuple, UnknownFormatError

    start_time = time.time()
    fileobject = io.StringIO(str(filecontent))
    try:
        structure_tuple = get_structure_tuple(fileobject, fileformat)
    except UnknownFormatError:
        logme(filecontent, fileformat, flask.request, call_source,
              reason = 'unknownformat')
        # Message passed to the next page
        flask.flash("Unknown format '{}'".format(fileformat))
        return flask.redirect(flask.url_for('input_structure'))
    except Exception:
        # There was an exception...
        import traceback
        logme(filecontent, fileformat, flask.request, call_source,
              reason = 'exception', extra = {
                'traceback': traceback.format_exc()
                })
        flask.flash("I tried my best, but I wasn't able to load your "
                "file in format '{}'...".format(fileformat))
        return flask.redirect(flask.url_for('input_structure'))

    if len(structure_tuple[1]) > MAX_NUMBER_OF_ATOMS:
        ## Structure too big
        logme(filecontent, fileformat, flask.request, call_source,
              reason = 'toolarge', extra={
                'number_of_atoms': len(structure_tuple[1])
                })
        flask.flash("Sorry, this online visualizer is limited to {} atoms "
            "in the input cell, while your structure has {} atoms."
            "".format(MAX_NUMBER_OF_ATOMS, len(structure_tuple[1])))
        return flask.redirect(flask.url_for('input_structure'))

    # Log the content in case of valid structure
    logme(filecontent, fileformat, flask.request, call_source,
          reason = 'OK', extra={
            'number_of_atoms': len(structure_tuple[1])
            })

    try:
        in_json_data = {
            'cell': structure_tuple[0],
            'scaled_coords': structure_tuple[1],
            'atomic_numbers': structure_tuple[2]
        }

        out_json_data, path_results = get_json_for_visualizer(
            in_json_data['cell'], 
            in_json_data['scaled_coords'],
            in_json_data['atomic_numbers'])

        raw_code_dict = copy.copy(out_json_data)
        for k in list(raw_code_dict.keys()):
            if k.startswith('explicit_'):
                raw_code_dict.pop(k)
            if k == 'segments':
                raw_code_dict.pop(k)
        raw_code_dict.pop('faces_data')
        raw_code_dict['primitive_lattice'] = path_results[
            'primitive_lattice'].tolist()
        raw_code_dict['primitive_positions'] = path_results[
            'primitive_positions'].tolist()
        primitive_positions_cartesian = np.dot(
            np.array(path_results['primitive_positions']),
            np.array(path_results['primitive_lattice']),
            ).tolist()
        primitive_positions_cartesian_refolded = np.dot(
            np.array(path_results['primitive_positions'])%1.,
            np.array(path_results['primitive_lattice']),
            ).tolist()
        raw_code_dict['primitive_positions_cartesian'] = \
            primitive_positions_cartesian

        # raw_code['primitive_types'] = path_results['primitive_types']
        primitive_symbols = [chemical_symbols[num] for num 
            in path_results['primitive_types']]
        raw_code_dict['primitive_symbols'] = primitive_symbols

        raw_code = json.dumps(raw_code_dict, indent=2)
        ## I manually escape it to then add <br> and pass it to a filter with
        ## |safe. I have to 'unicode' it otherwise it keeps escaping also the
        ## next replaces
        raw_code = str(flask.escape(raw_code)).replace(
            '\n', '<br>').replace(' ', '&nbsp;')

        kpoints = [[k, out_json_data['kpoints'][k][0], 
            out_json_data['kpoints'][k][1], out_json_data['kpoints'][k][2]] 
            for k in sorted(out_json_data['kpoints'])]
        kpoints_rel = [[k, out_json_data['kpoints_rel'][k][0], 
            out_json_data['kpoints_rel'][k][1], out_json_data['kpoints_rel'][k][2]] 
            for k in sorted(out_json_data['kpoints_rel'])]

        inputstructure_cell_vectors = [[idx, coords[0], coords[1], coords[2]]
            for idx, coords in 
            enumerate(in_json_data['cell'], start=1)
        ]

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
        center = (primitive_lattice[0] + primitive_lattice[1] + 
                  primitive_lattice[2])/2.
        cell_json = {
                "t": "UnitCell",
                "i": "s0",
                "o": (-center).tolist(),
                "x": (primitive_lattice[0]-center).tolist(),
                "y": (primitive_lattice[1]-center).tolist(),
                "z": (primitive_lattice[2]-center).tolist(),
                "xy": (primitive_lattice[0] + primitive_lattice[1] 
                       - center).tolist(),
                "xz": (primitive_lattice[0] + primitive_lattice[2] 
                       - center).tolist(),
                "yz": (primitive_lattice[1] + primitive_lattice[2] 
                       - center).tolist(),
                "xyz": (primitive_lattice[0] + primitive_lattice[1] 
                        + primitive_lattice[2] - center).tolist(),
            }
        atoms_json = [ 
                    {"l": label,
                    "x": pos[0]-center[0],
                    "y": pos[1]-center[1],
                    "z": pos[2]-center[2]} 
                    for label, pos in zip(
                            primitive_symbols, 
                            primitive_positions_cartesian_refolded)
                    ]
        # These will be passed to ChemDoodle
        json_content = {"s": [cell_json], 
                        "m": [{"a": atoms_json}]
                        }

        compute_time = time.time() - start_time        
    except Exception:
        import traceback
        logme(filecontent, fileformat, flask.request, call_source,
              reason = 'codeexception', extra={
                'traceback': traceback.extract_stack()})
        raise

    qe_pw = str(flask.escape(
        get_qe_pw(raw_code_dict, out_json_data))).replace(
            '\n', '<br>').replace(' ', '&nbsp;')
    qe_matdyn = str(flask.escape(
        get_qe_matdyn(raw_code_dict, out_json_data))).replace(
            '\n', '<br>').replace(' ', '&nbsp;')

    return flask.render_template(
        'visualizer.html', 
        jsondata=json.dumps(out_json_data),
        json_content=json.dumps(json_content),
        volume_ratio_prim=int(round(path_results['volume_original_wrt_prim'])),
        raw_code=raw_code,
        kpoints=kpoints,
        kpoints_rel=kpoints_rel,
        bravais_lattice=path_results['bravais_lattice'],
        bravais_lattice_extended=path_results['bravais_lattice_extended'],
        spacegroup_number=path_results['spacegroup_number'],
        spacegroup_international=path_results['spacegroup_international'],
        direct_vectors=direct_vectors,
        inputstructure_cell_vectors=inputstructure_cell_vectors,
        atoms_scaled=atoms_scaled,
        with_without_time_reversal= (
            "with" if path_results['has_inversion_symmetry'] 
            else "without"),
        atoms_cartesian=atoms_cartesian,
        reciprocal_primitive_vectors=reciprocal_primitive_vectors,
        suggested_path=suggested_path,
        qe_pw=qe_pw,
        qe_matdyn=qe_matdyn,
        compute_time=compute_time,
        seekpath_version=seekpath.__version__,
        spglib_version=spglib.__version__,
        time_reversal_note = (
            time_reversal_note if path_results['augmented_path'] 
            else ""),
        )


def get_qe_pw(raw_data, out_json_data):
    """
    Return the data in format of the QE pw.x input
    """
    lines = []

    lines.append("&CONTROL")
    lines.append("    calculation = 'bands'")
    lines.append("    <...>")
    lines.append("/")
    lines.append("&SYSTEM")
    lines.append("    ibrav = 0")
    lines.append("    nat = {}".format(
        len(raw_data["primitive_symbols"])))
    lines.append("    ntyp = {}".format(
        len(set(raw_data["primitive_symbols"]))))
    lines.append("    <...>")
    lines.append("/")
    lines.append("&ELECTRONS")
    lines.append("    <...>")
    lines.append("/")
    lines.append("ATOMIC_SPECIES")
    for s in sorted(set(
        raw_data["primitive_symbols"])):
        lines.append("{:4s} <MASS_HERE> <PSEUDO_HERE>.UPF".format(
            s))

    lines.append("ATOMIC_POSITIONS angstrom")
    for s, p in zip(
        raw_data["primitive_symbols"],
        raw_data["primitive_positions_cartesian"]):
        lines.append("{:4s} {:16.10f} {:16.10f} {:16.10f}".format(
            s, p[0], p[1], p[2]))

    lines.append("K_POINTS crystal")
    kplines = []
    for kp in out_json_data['explicit_kpoints_rel']:
        kplines.append("{:16.10f} {:16.10f} {:16.10f} 1".format(
            *kp))
    lines.append("{}".format(len(kplines)))
    lines += kplines

    lines.append("CELL_PARAMETERS angstrom")
    for v in raw_data['primitive_lattice']:
        lines.append("{:16.10f} {:16.10f} {:16.10f}".format(
            v[0], v[1], v[2]))


    return "\n".join(lines)

def get_qe_matdyn(raw_data, out_json_data):
    """
    Return the data in format of the QE matdyn.x input
    """
    return "Not implemented yet, sorry..."

@app.route('/')
def index():
    """
    Main view, redirect to input_structure
    """
    return flask.redirect(flask.url_for('input_structure'))

@app.route('/termsofuse/')
def termsofuse():
    """
    View for the terms of use
    """
    return flask.send_from_directory(view_folder, 'termsofuse.html')

@app.route('/bravaissymbol_explanation/')
def bravaissymbol_explanation():
    """
    View for the explanation of the Bravais symbol
    """
    return flask.send_from_directory(view_folder, 'bravaissymbol_explanation.html')


@app.route('/input_structure/')
def input_structure():
    """
    Input structure selection
    """
    return flask.render_template('visualizer_select.html')

@app.route('/static/js/<path:path>')
def send_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'js'), path)

@app.route('/static/img/<path:path>')
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'img'), path)

@app.route('/static/css/<path:path>')
def send_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'css'), path)

@app.route('/static/css/images/<path:path>')
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(os.path.join(static_folder, 
        'css', 'images'), path)

@app.route('/static/fonts/<path:path>')
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'fonts'), path)

@app.route('/process_structure/', methods=['GET', 'POST'])
def process_structure():
    """
    Process a structure (uploaded from POST request)
    """
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'structurefile' not in flask.request.files:
            return flask.redirect(flask.url_for('input_structure'))
        structurefile = flask.request.files['structurefile']
        fileformat = flask.request.form.get('fileformat', 'unknown')
        filecontent = structurefile.read()
        
        try:
            return process_structure_core(
                filecontent=filecontent, fileformat=fileformat,
                call_source="process_structure")
        except seekpath.hpkot.SymmetryDetectionError:
            flask.flash(
                "Unable to detect symmetry... "
                "Maybe you have overlapping atoms?")
            return flask.redirect(flask.url_for('input_structure'))
        except Exception:
            flask.flash(
                "Unable to process the structure, sorry...")
            return flask.redirect(flask.url_for('input_structure'))


    else: # GET Request
        return flask.redirect(flask.url_for('input_structure'))

@app.route('/process_example_structure/', methods=['GET', 'POST'])
def process_example_structure():
    """
    Process an example structure (example name from POST request)
    """
    if flask.request.method == 'POST':
        examplestructure = flask.request.form.get('examplestructure', '<none>')
        fileformat = "vasp"

        try:
            ext_bravais, withinv = valid_examples[examplestructure]
        except KeyError:
            flask.flash("Invalid example structure '{}'".format(
                examplestructure))
            return flask.redirect(flask.url_for('input_structure'))

        poscarfile = "POSCAR_inversion" if withinv else "POSCAR_noinversion"

        # I expect that the valid_examples dictionary already filters only 
        # existing files, so I don't try/except here
        with open(os.path.join(
                os.path.split(seekpath.__file__)[0],
                'hpkot', 'band_path_data', 
                ext_bravais, poscarfile)) as structurefile:
            filecontent = structurefile.read()
        
        return process_structure_core(
            filecontent=filecontent, fileformat=fileformat,
            call_source="process_example_structure[{}]".format(examplestructure))

    else: # GET Request
        return flask.redirect(flask.url_for('input_structure'))

if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of seekpath, not the installed one
    app.use_x_sendfile=False 
    app.run(debug=True)
