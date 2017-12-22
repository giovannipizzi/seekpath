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

import datetime
import flask
import os

from seekpath_web_module import (generate_log, FlaskRedirectException, logme,
                                 process_structure_core)


# This (undocumented) flag changes the style of the webpage (CSS, etc.)
# and decides whether some of the headers (e.g. the SeeK-path title) and the
# description of what seekpath can do should appear or not
#
# Options:
# - 'lite': simple version, not title, no info description, different CSS
# - anything else: default
#
# How to pass: with Apache, when forwarding, in a ReverseProxy section, add
#   RequestHeader set X-Seekpath-Style lite
def get_style_version(request):
    return request.environ.get("HTTP_X_SEEKPATH_STYLE", "")


import logging, logging.handlers
logger = logging.getLogger("seekpath_server")

logHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(
        os.path.split(os.path.realpath(__file__))[0], 'logs', 'requests.log'),
    when='midnight')
formatter = logging.Formatter(
    '[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)


class ConfigurationError(Exception):
    pass


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

if __name__ == "__main__":
    # If run manually (=> debug/development mode),
    # use the local version of seekpath, not the installed one
    import sys
    sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.pardir))
# Need to import all three, as they are used later when seekpath
# is passed as a variable - otherwise, the function will not use it
import seekpath, seekpath.hpkot, seekpath.brillouinzone, seekpath.brillouinzone.brillouinzone
from seekpath.hpkot import SymmetryDetectionError

static_folder = os.path.join(
    os.path.split(os.path.realpath(__file__))[0], 'static')
view_folder = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'view')
app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
directory = os.path.split(os.path.realpath(__file__))[0]
try:
    with open(os.path.join(directory, 'SECRET_KEY')) as f:
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


def get_visualizer_select_template(request):
    if get_style_version(request) == 'lite':
        return 'visualizer_select_lite.html'
    else:
        return 'visualizer_select.html'


def get_visualizer_template(request):
    if get_style_version(request) == 'lite':
        return 'visualizer_lite.html'
    else:
        return 'visualizer.html'


logger.debug("Start")

# From http://arusahni.net/blog/2014/03/flask-nocache.html
## Add @nocache right between @app.route and the 'def' line
from functools import wraps, update_wrapper


def nocache(view):

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


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
    return flask.send_from_directory(view_folder,
                                     'bravaissymbol_explanation.html')


@app.route('/input_structure/')
def input_structure():
    """
    Input structure selection
    """
    return flask.render_template(get_visualizer_select_template(flask.request))


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
    return flask.send_from_directory(
        os.path.join(static_folder, 'css', 'images'), path)


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
            data_for_template = process_structure_core(
                filecontent=filecontent,
                fileformat=fileformat,
                seekpath_module=seekpath,
                call_source="process_structure",
                logger=logger,
                flask_request=flask.request)
            return flask.render_template(
                get_visualizer_template(flask.request), **data_for_template)
        except FlaskRedirectException as e:
            flask.flash(e.message)
            return flask.redirect(flask.url_for('input_structure'))
        except SymmetryDetectionError:
            flask.flash("Unable to detect symmetry... "
                        "Maybe you have overlapping atoms?")
            return flask.redirect(flask.url_for('input_structure'))
        except Exception:
            flask.flash("Unable to process the structure, sorry...")
            return flask.redirect(flask.url_for('input_structure'))

    else:  # GET Request
        return flask.redirect(flask.url_for('input_structure'))


@app.route('/process_example_structure/', methods=['GET', 'POST'])
def process_example_structure():
    """
    Process an example structure (example name from POST request)
    """
    if flask.request.method == 'POST':
        examplestructure = flask.request.form.get('examplestructure', '<none>')
        fileformat = "vasp-ase"

        try:
            ext_bravais, withinv = valid_examples[examplestructure]
        except KeyError:
            flask.flash(
                "Invalid example structure '{}'".format(examplestructure))
            return flask.redirect(flask.url_for('input_structure'))

        poscarfile = "POSCAR_inversion" if withinv else "POSCAR_noinversion"

        # I expect that the valid_examples dictionary already filters only
        # existing files, so I don't try/except here
        with open(
                os.path.join(
                    os.path.split(seekpath.__file__)[0], 'hpkot',
                    'band_path_data', ext_bravais,
                    poscarfile)) as structurefile:
            filecontent = structurefile.read()

        try:
            data_for_template = process_structure_core(
                filecontent=filecontent,
                fileformat=fileformat,
                seekpath_module=seekpath,
                call_source="process_example_structure[{}]".format(
                    examplestructure),
                logger=logger,
                flask_request=flask.request)
            return flask.render_template(
                get_visualizer_template(flask.request), **data_for_template)
        except FlaskRedirectException as e:
            flask.flash(e.message)
            return flask.redirect(flask.url_for('input_structure'))

    else:  # GET Request
        return flask.redirect(flask.url_for('input_structure'))


if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of seekpath, not the installed one
    app.use_x_sendfile = False
    app.run(debug=True)
