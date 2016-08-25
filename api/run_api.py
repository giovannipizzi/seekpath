#!/usr/bin/env python
import flask
app = flask.Flask(__name__)
import tempfile

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

@app.route('/process_structure/', methods=['GET', 'POST'])
def process_structure():
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'structurefile' not in flask.request.files:
            #flash('No file part')
            return flask.redirect(request.url)
        structurefile = flask.request.files['structurefile']
        fileformat = flask.request.form.get('fileformat', 'unknown')
        fileobject = StringIO.StringIO(structurefile.read())
        #with tempfile.NamedTemporaryFile() as f:
        #    structurefile.save(f.name)
        #    print f.name
            
        if fileformat == 'vasp':
            import ase.io.vasp
            asestructure = ase.io.vasp.read_vasp(fileobject)
        else:
            content = "Unknown format '{}'".format(fileformat)
            # Return immediately (TODO: change page)
            return flask.render_template('basic_visualizer.html', 
                                         content=content)

        json_data = {
            'cell': asestructure.cell.tolist(),
            'scaled_coords': asestructure.get_scaled_positions().tolist(),
            'symbols': asestructure.get_chemical_symbols(),
        }
        content = json.dumps(json_data, indent=2)
        content = content.replace('\n', '<br>').replace(' ', '&nbsp;')
        content = "<code>{}</code>".format(content)

        return flask.render_template('basic_visualizer.html', 
                                     content=content)
        

    else:
        return flask.send_from_directory('view', 'process_structure.html')


if __name__ == "__main__":
    app.run(debug=True)
