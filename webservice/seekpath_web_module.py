"""
Most of the functions needed by the web service are here. 
In seekpath_app.py we just keep the main web logic.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import zip
import os

import copy
import numpy as np
import time, datetime

from ase.data import chemical_symbols
import json
import io

import jinja2
import spglib  # Mainly to get its version


class FlaskRedirectException(Exception):
    """
    Class used to return immediately with a flash message and a redirect.
    """
    pass


MAX_NUMBER_OF_ATOMS = 1000
time_reversal_note = ("The second half of the path is required only if "
                      "the system does not have time-reversal symmetry")


def logme(logger, *args, **kwargs):
    """
    Log information on the passed logger. 

    See docstring of generate_log for more info on the
    accepted kwargs.

    :param logger: a valid logger. If you pass `None`, no log is output.
    """
    if logger is not None:
        logger.debug(generate_log(*args, **kwargs))


def generate_log(filecontent,
                 fileformat,
                 request,
                 call_source,
                 reason,
                 extra={}):
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

    logdict = {
        'data': data,
        'reason': reason,
        'request': str(request.headers),
        'call_source': call_source,
        'source': request.headers.get('X-Forwarded-For', request.remote_addr),
        'time': datetime.datetime.now().isoformat()
    }
    logdict.update(extra)
    return json.dumps(logdict)


def get_json_for_visualizer(cell, relcoords, atomic_numbers, seekpath_module):
    #from seekpath_module import hpkot, brillouinzone
    hpkot = seekpath_module.hpkot
    brillouinzone = seekpath_module.brillouinzone

    system = (np.array(cell), np.array(relcoords), np.array(atomic_numbers))
    res = hpkot.get_path(system, with_time_reversal=False)

    real_lattice = res['primitive_lattice']
    #rec_lattice = np.linalg.inv(real_lattice).T # Missing 2pi!
    rec_lattice = np.array(hpkot.tools.get_reciprocal_cell_rows(real_lattice))
    b1, b2, b3 = rec_lattice

    faces_data = brillouinzone.brillouinzone.get_BZ(b1=b1, b2=b2, b3=b3)

    response = {}
    response['faces_data'] = faces_data
    response['b1'] = b1.tolist()
    response['b2'] = b2.tolist()
    response['b3'] = b3.tolist()
    ## Convert to absolute
    response['kpoints'] = {
        k: (v[0] * b1 + v[1] * b2 + v[2] * b3).tolist()
        for k, v in res['point_coords'].items()
    }
    response['kpoints_rel'] = {
        k: [v[0], v[1], v[2]] for k, v in res['point_coords'].items()
    }
    response['path'] = res['path']

    # It should use the same logic, so give the same cell as above
    res_explicit = seekpath_module.get_explicit_k_path(system,
                                                       with_time_reversal=False)
    for k in res_explicit:
        if k == 'segments' or k.startswith('explicit_'):
            if isinstance(res_explicit[k], np.ndarray):
                response[k] = res_explicit[k].tolist()
            else:
                response[k] = res_explicit[k]

    if np.sum(
            np.abs(
                np.array(res_explicit['reciprocal_primitive_lattice']) -
                np.array(res['reciprocal_primitive_lattice']))) > 1.e-7:
        raise AssertionError("Got different reciprocal cells...")

    # Response for JS, and path_results
    return response, res


def process_structure_core(filecontent,
                           fileformat,
                           seekpath_module,
                           call_source="",
                           logger=None,
                           flask_request=None):
    """
    The main function that generates the data to be sent back to the view.
    
    :param filecontent: The file content (string)
    :param fileformat: The file format (string), among the accepted formats
    :param seekpath_module: the seekpath module. The reason for passing it
         is that, when running in debug mode, you want to get the local 
         seekpath rather than the installed one.
    :param call_source: a string identifying the source (i.e., who called
       this function). This is a string, mainly for logging reasons.
    :param logger: if not None, should be a valid logger, that is used
       to output useful log messages.
    :param flask_request: if logger is not None, pass also the flask.request
       object to help in logging.

    :return: this function calls directly flask methods and returns flask 
        objects

    :raise: FlaskRedirectException if there is an error that requires
        to redirect the the main selection page. The Exception message
        is the message to be flashed via Flask (or in general shown to
        the user).
    """
    from structure_importers import get_structure_tuple, UnknownFormatError

    start_time = time.time()
    fileobject = io.StringIO(str(filecontent))
    form_data = dict(flask_request.form)
    try:
        structure_tuple = get_structure_tuple(fileobject,
                                              fileformat,
                                              extra_data=form_data)
    except UnknownFormatError:
        logme(logger,
              filecontent,
              fileformat,
              flask_request,
              call_source,
              reason='unknownformat',
              extra={
                  'form_data': form_data,
              })
        raise FlaskRedirectException("Unknown format '{}'".format(fileformat))
    except Exception:
        # There was an exception...
        import traceback
        logme(logger,
              filecontent,
              fileformat,
              flask_request,
              call_source,
              reason='exception',
              extra={
                  'traceback': traceback.format_exc(),
                  'form_data': form_data,
              })
        raise FlaskRedirectException(
            "I tried my best, but I wasn't able to load your "
            "file in format '{}'...".format(fileformat))

    if len(structure_tuple[1]) > MAX_NUMBER_OF_ATOMS:
        ## Structure too big
        logme(logger,
              filecontent,
              fileformat,
              flask_request,
              call_source,
              reason='toolarge',
              extra={
                  'number_of_atoms': len(structure_tuple[1]),
                  'form_data': form_data,
              })
        raise FlaskRedirectException(
            "Sorry, this online visualizer is limited to {} atoms "
            "in the input cell, while your structure has {} atoms."
            "".format(MAX_NUMBER_OF_ATOMS, len(structure_tuple[1])))

    # Log the content in case of valid structure
    logme(logger,
          filecontent,
          fileformat,
          flask_request,
          call_source,
          reason='OK',
          extra={
              'number_of_atoms': len(structure_tuple[1]),
              'form_data': form_data,
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
            in_json_data['atomic_numbers'],
            seekpath_module=seekpath_module)

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
        inputstructure_positions_cartesian = np.dot(
            np.array(in_json_data['scaled_coords']),
            np.array(in_json_data['cell']),
        ).tolist()
        primitive_positions_cartesian = np.dot(
            np.array(path_results['primitive_positions']),
            np.array(path_results['primitive_lattice']),
        ).tolist()
        primitive_positions_cartesian_refolded = np.dot(
            np.array(path_results['primitive_positions']) % 1.,
            np.array(path_results['primitive_lattice']),
        ).tolist()
        raw_code_dict['primitive_positions_cartesian'] = \
            primitive_positions_cartesian

        # raw_code['primitive_types'] = path_results['primitive_types']
        primitive_symbols = [
            chemical_symbols[num] for num in path_results['primitive_types']
        ]
        raw_code_dict['primitive_symbols'] = primitive_symbols

        raw_code = json.dumps(raw_code_dict, indent=2)
        ## I manually escape it to then add <br> and pass it to a filter with
        ## |safe. I have to 'unicode' it otherwise it keeps escaping also the
        ## next replaces
        raw_code = str(jinja2.escape(raw_code)).replace('\n', '<br>').replace(
            ' ', '&nbsp;')

        kpoints = [[
            k, out_json_data['kpoints'][k][0], out_json_data['kpoints'][k][1],
            out_json_data['kpoints'][k][2]
        ] for k in sorted(out_json_data['kpoints'])]
        kpoints_rel = [[
            k, out_json_data['kpoints_rel'][k][0],
            out_json_data['kpoints_rel'][k][1],
            out_json_data['kpoints_rel'][k][2]
        ] for k in sorted(out_json_data['kpoints_rel'])]

        inputstructure_cell_vectors = [[
            idx, coords[0], coords[1], coords[2]
        ] for idx, coords in enumerate(in_json_data['cell'], start=1)]
        inputstructure_symbols = [
            chemical_symbols[num] for num in in_json_data['atomic_numbers']
        ]
        inputstructure_atoms_scaled = [
            [label, coords[0], coords[1], coords[2]] for label, coords in zip(
                inputstructure_symbols, in_json_data['scaled_coords'])
        ]
        inputstructure_atoms_cartesian = [[
            label, coords[0], coords[1], coords[2]
        ] for label, coords in zip(inputstructure_symbols,
                                   inputstructure_positions_cartesian)]

        direct_vectors = [[idx, coords[0], coords[1], coords[2]]
                          for idx, coords in enumerate(
                              path_results['primitive_lattice'], start=1)]

        reciprocal_primitive_vectors = [[
            idx, coords[0], coords[1], coords[2]
        ] for idx, coords in enumerate(
            path_results['reciprocal_primitive_lattice'], start=1)]

        atoms_scaled = [
            [label, coords[0], coords[1], coords[2]] for label, coords in zip(
                primitive_symbols, path_results['primitive_positions'])
        ]

        atoms_cartesian = [[label, coords[0], coords[1], coords[2]]
                           for label, coords in zip(
                               primitive_symbols, primitive_positions_cartesian)
                          ]

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
        xsfstructure = []
        xsfstructure.append("CRYSTAL")
        xsfstructure.append("PRIMVEC")
        for vector in primitive_lattice:
            xsfstructure.append("{} {} {}".format(vector[0], vector[1],
                                                  vector[2]))
        xsfstructure.append("PRIMCOORD")
        xsfstructure.append("{} 1".format(
            len(primitive_positions_cartesian_refolded)))
        for atom_num, pos in zip(path_results['primitive_types'],
                                 primitive_positions_cartesian_refolded):
            xsfstructure.append("{} {} {} {}".format(atom_num, pos[0], pos[1],
                                                     pos[2]))
        xsfstructure = "\n".join(xsfstructure)

        compute_time = time.time() - start_time
    except Exception:
        import traceback
        logme(logger,
              filecontent,
              fileformat,
              flask_request,
              call_source,
              reason='codeexception',
              extra={
                  'traceback': traceback.extract_stack(),
                  'form_data': form_data,
              })
        raise

    qe_pw = str(jinja2.escape(get_qe_pw(raw_code_dict, out_json_data))).replace(
        '\n', '<br>').replace(' ', '&nbsp;')
    qe_matdyn = str(jinja2.escape(get_qe_matdyn(
        raw_code_dict, out_json_data))).replace('\n',
                                                '<br>').replace(' ', '&nbsp;')
    cp2k = str(jinja2.escape(get_cp2k(raw_code_dict))).replace(
        '\n', '<br>').replace(' ', '&nbsp;')
    crystal = str(jinja2.escape(get_crystal(raw_code_dict))).replace(
        '\n', '<br>').replace(' ', '&nbsp;')
    vasp_gga = str(jinja2.escape(get_vasp_gga(raw_code_dict))).replace(
        '\n', '<br>').replace(' ', '&nbsp;')
    vasp_gen = str(jinja2.escape(get_vasp_gen(out_json_data))).replace(
        '\n', '<br>').replace(' ', '&nbsp;')

    return dict(
        jsondata=json.dumps(out_json_data),
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
        inputstructure_atoms_scaled=inputstructure_atoms_scaled,
        inputstructure_atoms_cartesian=inputstructure_atoms_cartesian,
        atoms_scaled=atoms_scaled,
        with_without_time_reversal=(
            "with" if path_results['has_inversion_symmetry'] else "without"),
        atoms_cartesian=atoms_cartesian,
        reciprocal_primitive_vectors=reciprocal_primitive_vectors,
        suggested_path=suggested_path,
        qe_pw=qe_pw,
        qe_matdyn=qe_matdyn,
        cp2k=cp2k,
        crystal=crystal,
        vasp_gga=vasp_gga,
        vasp_gen=vasp_gen,
        compute_time=compute_time,
        seekpath_version=seekpath_module.__version__,
        spglib_version=spglib.__version__,
        time_reversal_note=(time_reversal_note
                            if path_results['augmented_path'] else ""),
        xsfstructure=xsfstructure)


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
    lines.append("    nat = {}".format(len(raw_data["primitive_symbols"])))
    lines.append("    ntyp = {}".format(len(set(
        raw_data["primitive_symbols"]))))
    lines.append("    <...>")
    lines.append("/")
    lines.append("&ELECTRONS")
    lines.append("    <...>")
    lines.append("/")
    lines.append("ATOMIC_SPECIES")
    for s in sorted(set(raw_data["primitive_symbols"])):
        lines.append("{:4s} <MASS_HERE> <PSEUDO_HERE>.UPF".format(s))

    lines.append("ATOMIC_POSITIONS angstrom")
    for s, p in zip(raw_data["primitive_symbols"],
                    raw_data["primitive_positions_cartesian"]):
        lines.append("{:4s} {:16.10f} {:16.10f} {:16.10f}".format(
            s, p[0], p[1], p[2]))

    lines.append("K_POINTS crystal")
    kplines = []
    for kp in out_json_data['explicit_kpoints_rel']:
        kplines.append("{:16.10f} {:16.10f} {:16.10f} 1".format(*kp))
    lines.append("{}".format(len(kplines)))
    lines += kplines

    lines.append("CELL_PARAMETERS angstrom")
    for v in raw_data['primitive_lattice']:
        lines.append("{:16.10f} {:16.10f} {:16.10f}".format(v[0], v[1], v[2]))

    return "\n".join(lines)


def get_qe_matdyn(raw_data, out_json_data):
    """
    Return the data in format of the QE matdyn.x input
    """
    return "Not implemented yet, sorry..."


def get_cp2k(raw_data):
    """
    Return the data in format of a CP2K input
    """
    template = jinja2.Template("""
&GLOBAL
   RUN_TYPE ENERGY
   <...>
&END GLOBAL

&FORCE_EVAL
   <...>

   &DFT
      <...>

      &QS
         EXTRAPOLATION USE_GUESS ! required for K-Point sampling
      &END QS

      &POISSON
         PERIODIC XYZ
      &END POISSON

      &PRINT
         &BAND_STRUCTURE
            FILE_NAME <NAME_HERE>.bs

            {% for s in raw.path -%}
            &KPOINT_SET
               UNITS B_VECTOR
               SPECIAL_POINT {{ '%5s' % s[0] }} {%- for c in raw.kpoints_rel[s[0]] %} {{ '%16.10f' % c }}{% endfor %}
               SPECIAL_POINT {{ '%5s' % s[1] }} {%- for c in raw.kpoints_rel[s[1]] %} {{ '%16.10f' % c }}{% endfor %}
               NPOINTS 10
            &END KPOINT_SET
            {% endfor %}
         &END BAND_STRUCTURE
      &END PRINT

      &KPOINTS
         <...>
      &END KPOINTS
   &END DFT

   &SUBSYS
      ! Important: use the cell and coordinates provided here instead of the original ones
      &CELL
         {%- for s, v in zip(['A', 'B', 'C'], raw.primitive_lattice) %}
         {{ '%4s' % s }} [angstrom] {%- for c in v %} {{ '%16.10f' % c }}{% endfor %}
         {%- endfor %}
         PERIODIC XYZ
      &END CELL
      &COORD
         {%- for s, v in zip(raw.primitive_symbols, raw.primitive_positions_cartesian) %}
         {{ '%4s' % s }} {%- for c in v %} {{ '%16.10f' % c }}{% endfor %}
         {%- endfor %}
      &END COORD

      {% for s in set(raw.primitive_symbols) -%}
      &KIND {{ s }}
         ELEMENT {{ s }}
         BASIS_SET <BS_NAME_HERE>
         POTENTIAL <PP_NAME_HERE>
      &END KIND
      {% endfor %}
   &END SUBSYS
&END FORCE_EVAL
""")
    return template.render(
        raw=raw_data,  # export the complete raw data to the template
        zip=zip,
        set=set  # add zip and set to the template environment for some loops
    )


def get_crystal(raw_data):
    """
    Return the data in format of a CRYSTAL d3 input
    """

    def float_to_fraction(x, error=0.000001):
        '''
        1D float np.array to 1D fraction (int) array
        Modified from ref: https://stackoverflow.com/questions/5124743/algorithm-for-simplifying-decimal-to-fractions
        '''
        out = np.empty([len(x), 2], dtype=np.int)
        for i, value in enumerate(x):
            if value < error:
                out[i] = 0, 1
            elif 1 - error < value:
                out[i] = 1, 1
            else:
                # The lower fraction is 0/1
                lower_n = 0
                lower_d = 1
                # The upper fraction is 1/1
                upper_n = 1
                upper_d = 1
                while True:
                    # The middle fraction is (lower_n + upper_n) / (lower_d + upper_d)
                    middle_n = lower_n + upper_n
                    middle_d = lower_d + upper_d
                    # If value + error < middle

                    if middle_d * (value + error) < middle_n:
                        # middle is our new upper
                        upper_n = middle_n
                        upper_d = middle_d
                    # Else If middle < value - error
                    elif middle_n < (value - error) * middle_d:
                        # middle is our new lower
                        lower_n = middle_n
                        lower_d = middle_d
                    # Else middle is our best fraction
                    else:
                        out[i] = middle_n, middle_d
                        break
        return out

    lines = []
    lines.append("BAND")
    lines.append("<...>     !Title")
    kpath = []
    klabel = []
    for s in raw_data['path']:
        c0 = raw_data['kpoints_rel'][s[0]]
        c1 = raw_data['kpoints_rel'][s[1]]
        klabel.append([s[0], s[1]])
        kpath.append([c0, c1])

    npath = len(kpath)
    kpath = np.float64(kpath)
    kpath_flat = kpath.flatten()
    fraction_kpath = float_to_fraction(kpath_flat)
    numerator = fraction_kpath[:, 0]
    denominator = fraction_kpath[:, 1]
    shrinking_fac = np.lcm.reduce(denominator)
    kpath_new = shrinking_fac * kpath_flat
    kpath_new = np.int64(kpath_new.round().reshape(npath, 2, -1))
    lines.append(
        "{:d} {:d} 100 <...> <...> 1 0     !<...> - <...>: 1st band - last band"
        .format(npath, shrinking_fac))
    for i, path in enumerate(kpath_new):
        c0 = path[0]
        c1 = path[1]

        lines.append(
            "{:2d} {:2d} {:2d}  {:2d} {:2d} {:2d}    {:2s} -> {:2s}".format(
                c0[0], c0[1], c0[2], c1[0], c1[1], c1[2], klabel[i][0],
                klabel[i][1]))

    return "\n".join(lines)


def get_vasp_gga(raw_data):
    """
    Return the KPOINTS data in format of a VASP input for LDA or GGA functional
    """
    lines = []
    lines.append("Special k-points for band structure")
    lines.append("<...>  ! intersections ")
    lines.append("line-mode")
    lines.append("reciprocal")
    kpath = []
    for s in raw_data['path']:
        c0 = raw_data['kpoints_rel'][s[0]]
        c1 = raw_data['kpoints_rel'][s[1]]
        lines.append("{:16.10f} {:16.10f} {:16.10f} 1    {:2s}".format(
            c0[0], c0[1], c0[2], s[0]))
        lines.append("{:16.10f} {:16.10f} {:16.10f} 1    {:2s}".format(
            c1[0], c1[1], c1[2], s[1]))
        lines.append("\n")

    return "\n".join(lines)


def get_vasp_gen(out_json_data):
    """
    Return the KPOINTS data in format of a general VASP input (GGA, Hybrid, GW)
    """
    lines = []
    lines.append("Explicit k-points list for band structure")
    kplines = []
    for kp in out_json_data['explicit_kpoints_rel']:
        kplines.append("{:16.10f} {:16.10f} {:16.10f} 0".format(*kp))
    nkpts = len(kplines)
    lines.append(
        "<...>  !Total number of k-points = {:2d} + No. of k-points from IBZKPT file"
        .format(nkpts))
    lines.append("reciprocal")
    lines.append("<...Copy the kpoints coordinates block from IBZKPT here...>")
    lines.append("\n")
    lines += kplines

    return "\n".join(lines)
