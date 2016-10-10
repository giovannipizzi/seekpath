# -*- coding: utf-8 -*-
"""
This code has been adapted from 
AiiDA (www.aiida.net), also released under an MIT license.

The AiiDA license reads:

The MIT License (MIT)

Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE
(Theory and Simulation of Materials (THEOS) and National Centre for 
Computational Design and Discovery of Novel Materials (NCCR MARVEL)),
Switzerland and ROBERT BOSCH LLC, USA. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import numpy as np
import seekpath.util
from seekpath.util import atoms_num_dict

bohr_to_ang = 0.52917720859

class InputValidationError(ValueError):
    """
    Exception raised when there are problems
    """
    pass

def get_fortfloat(key, txt, be_case_sensitive=True):
    """
    Matches a fortran compatible specification of a float behind a defined key in a string.
    :param key: The key to look for
    :param txt: The string where to search for the key
    :param be_case_sensitive: An optional boolean whether to search case-sensitive, defaults to ``True``

    If abc is a key, and f is a float, number, than this regex
    will match t and return f in the following cases:

    *   charsbefore, abc = f, charsafter
    *   charsbefore
        abc = f
        charsafter
    *   charsbefore, abc = f
        charsafter

    and vice-versa.
    If no float is matched, returns None

    Exampes of matchable floats are:

    *   0.1d2
    *   0.D-3
    *   .2e1
    *   -0.23
    *   23.
    *   232
    """
    import re
    pattern = """
        [\n,]                       # key - value pair can be prepended by comma or start
        [ \t]*                      # in a new line and some optional white space
        {}                          # the key goes here
        [ \t]*                      # Optional white space between key and equal sign
        =                           # Equals, you can put [=:,] if you want more specifiers
        [ \t]*                      # optional white space between specifier and float
        (?P<float>                  # Universal float pattern
            ( \d*[\.]\d+  |  \d+[\.]?\d* )
            ([ E | D | e | d ] [+|-]? \d+)?
        )
        [ \t]*[,\n,#]               # Can be followed by comma, end of line, or a comment
        """.format(key)
    REKEYS = re.X | re.M if be_case_sensitive else re.X | re.M | re.I
    match = re.search(
        pattern,
        txt,
        REKEYS)
    if not match:
        return None
    else:
        return float(match.group('float').replace('d', 'e').replace('D', 'e'))


def read_qeinp(fileobject):
    """
    Function that receives a file-like object containing a QE input file, and
    returns a tuple as accepted by SPGlib.
    This function can deal with ibrav being set different from 0 and the cell 
    being defined with celldm(n) or A,B,C, cosAB etc.
    """
    import re

    # This regular expression finds the block where Atomic positions are defined:
    pos_block_regex = re.compile(r"""
        ^ \s* ATOMIC_POSITIONS \s*                      # Atomic positions start with that string
        [{(]? \s* (?P<units>\S+?)? \s* [)}]? \s* $\n    # The units are after the string in optional brackets
        (?P<positions>                                  # This is the block of positions
            (
                (
                    \s*                                 # White space in front of the element spec is ok
                    (
                        [A-Za-z]+[A-Za-z0-9]{0,2}       # Element spec
                        (
                            \s+                         # White space in front of the number
                            [-|+]?                      # Plus or minus in front of the number (optional)
                            (
                                (
                                    \d*                 # optional decimal in the beginning .0001 is ok, for example
                                    [\.]                # There has to be a dot followed by
                                    \d+                 # at least one decimal
                                )
                                |                       # OR
                                (
                                    \d+                 # at least one decimal, followed by
                                    [\.]?               # an optional dot ( both 1 and 1. are fine)
                                    \d*                 # And optional number of decimals (1.00001)
                                )                        # followed by optional decimals
                            )
                            ([E|e|d|D][+|-]?\d+)?       # optional exponents E+03, e-05
                        ){3}                            # I expect three float values
                        ((\s+[0-1]){3}\s*)?             # Followed by optional ifpos
                        \s*                             # Followed by optional white space
                        |
                        \#.*                            # If a line is commented out, that is also ok
                        |
                        \!.*                            # Comments also with excl. mark in fortran
                    )
                    |                                   # OR
                    \s*                                 # A line only containing white space
                 )
                [\n]                                    # line break at the end
            )+                                          # A positions block should be one or more lines
        )
        """, re.X | re.M)

    # This regular expression finds the each position in a block of positions:
    # Matches eg: Li 0.21212e-3  2.d0 -23312.
    pos_regex = re.compile(r"""
        ^                                       # Linestart
        [ \t]*                                  # Optional white space
        (?P<sym>[A-Za-z]+[A-Za-z0-9]{0,2})\s+   # get the symbol, max 3 chars, starting with a char
        (?P<x>                                  # Get x
            [\-|\+]?(\d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        [ \t]+
        (?P<y>                                  # Get y
            [\-|\+]?(\d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        [ \t]+
        (?P<z>                                  # Get z
            [\-|\+]?(\d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        """, re.X | re.M)
    # Find the block for the cell
    cell_block_regex = re.compile(r"""
        ^ [ \t]*
        CELL_PARAMETERS [ \t]*
        [{(]? \s* (?P<units>[a-z]*) \s* [)}]? \s* [\n]
        (?P<cell>
        (
            (
                \s*             # White space in front of the element spec is ok
                (
                    (
                       \s+       # White space in front of the number
                        [-|+]?   # Plus or minus in front of the number (optional)
                        (\d*     # optional decimal in the beginning .0001 is ok, for example
                        [\.]     # There has to be a dot followed by
                        \d+)     # at least one decimal
                        |        # OR
                        (\d+     # at least one decimal, followed by
                        [\.]?    # an optional dot
                        \d*)     # followed by optional decimals
                        ([E|e|d|D][+|-]?\d+)?  # optional exponents E+03, e-05, d0, D0
                    ){3}         # I expect three float values
                    |
                    \#
                    |
                    !            # If a line is commented out, that is also ok
                )
                .*               # I do not care what is after the comment or the vector
                |                # OR
                \s*              # A line only containing white space
             )
            [\n]                 # line break at the end
        ){3}                     # I need exactly 3 vectors
    )
    """, re.X | re.M)

    # Matches each vector inside the cell block
    cell_vector_regex = re.compile(r"""
        ^                        # Linestart
        [ \t]*                   # Optional white space
        (?P<x>                   # Get x
            [\-|\+]? ( \d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        [ \t]+
        (?P<y>                   # Get y
            [\-|\+]? (\d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        [ \t]+
        (?P<z>                   # Get z
            [\-|\+]? (\d*[\.]\d+ | \d+[\.]?\d*)
            ([E|e|d|D][+|-]?\d+)?
        )
        """, re.X | re.M)

    # Finds the ibrav
    ibrav_regex = re.compile(
        'ibrav [ \t]* \= [ \t]*(?P<ibrav>\-?[ \t]* \d{1,2})', re.X)

    # Match the block where atomic species are defined:
    atomic_species_block_regex = re.compile("""
        ATOMIC_SPECIES \s+       # Prepended by ATOMIC_SPECIES
        (?P<block>
            ([ \t]*              # Space at line beginning
            [A-Za-z0-9]+         # tag for atom, max 3 characters
            [ \t]+               # Space
            ( \d*[\.]\d+  | \d+[\.]?\d* )
            ([D|d|E|e][+|-]?\d+)?                   # Mass
            [ \t]+                                  # Space
            \S+ \.(UPF | upf)                       # Pseudofile
            \s+)+
         )
         """, re.X | re.M)

    # Matches each atomic species inside the atomic specis block:
    atomic_species_regex = re.compile("""
        ^[ \t]*                  # Space at line beginning
        (?P<tag>
            [A-Za-z0-9]+         # tag for atom, max 3 characters
        )
            [ \t]+               # Space
        (?P<mass>                # Mass
            ( \d*[\.]\d+  | \d+[\.]?\d* )
            ([D|d|E|e][+|-]?\d+)?
        )
            [ \t]+               # Space
        (?P<pseudo>
            \S+ \.(UPF | upf)    # Pseudofile
        )
        """, re.X | re.M)

    valid_elements_regex = re.compile("""
        (?P<ele>
H  | He |
Li | Be | B  | C  | N  | O  | F  | Ne |
Na | Mg | Al | Si | P  | S  | Cl | Ar |
K  | Ca | Sc | Ti | V  | Cr | Mn | Fe | Co | Ni | Cu | Zn | Ga | Ge | As | Se | Br | Kr |
Rb | Sr | Y  | Zr | Nb | Mo | Tc | Ru | Rh | Pd | Ag | Cd | In | Sn | Sb | Te | I  | Xe |
Cs | Ba | Hf | Ta | W  | Re | Os | Ir | Pt | Au | Hg | Tl | Pb | Bi | Po | At | Rn |
Fr | Ra | Rf | Db | Sg | Bh | Hs | Mt |

La | Ce | Pr | Nd | Pm | Sm | Eu | Gd | Tb | Dy | Ho | Er | Tm | Yb | Lu | # Lanthanides
Ac | Th | Pa | U  | Np | Pu | Am | Cm | Bk | Cf | Es | Fm | Md | No | Lr | # Actinides
        )
        [^a-z]  # Any specification of an element is followed by some number
                # or capital letter or special character.
    """, re.X)

    txt = fileobject.read()

    #########  THE CELL ################

    # get ibrav and check if it is valid
    ibrav = int(ibrav_regex.search(txt).group('ibrav'))
    valid_ibravs = range(15) + [-5, -9, -12]
    if ibrav not in valid_ibravs:
        raise InputValidationError(
            'I found ibrav = {} in input, \n'
            'but it is not among the valid values\n'
            '{}'.format(ibrav, valid_ibravs))

    # First case, ibrav is 0
    if ibrav == 0:
        # The cell is defined explicitly in a block CELL_PARAMETERS
        # Match the cell block using the regex defined above:
        match = cell_block_regex.search(txt)
        if match is None:
            raise InputValidationError(
                'ibrav was found to be 0\n',
                'but I did not find the necessary block of CELL_PARAMETERS\n'
                'in the file'
            )
        valid_cell_units = ('angstrom', 'bohr', 'alat')

        # Check if unit was matched, default is bohr (a.u.)
        cell_unit = match.group('units').lower() or 'bohr'
        if cell_unit not in valid_cell_units:
            raise InputValidationError(
                '{} is not a valid  cell unit.\n'
                'Valid cell units are: {}'.format(cell_unit, valid_cell_units)
            )
        # cell was matched, transform to np.array:
        cell = np.array(
            [
                [float(match.group(i).replace('D', 'e').replace('d', 'e'))
                 for i in ('x', 'y', 'z')
                 ]
                for match
                in cell_vector_regex.finditer(match.group('cell'))
                ]
        )

        # Now, we do the convert the cell to the right units (we want angstrom):
        if cell_unit == 'angstrom':
            conversion = 1.
        elif cell_unit == 'bohr':
            conversion = bohr_to_ang
        elif cell_unit == 'alat':
            # Cell units are defined with respect to atomic lattice
            # defined either under key A or celldm(1),
            celldm1 = get_fortfloat('celldm\(1\)', txt)
            a = get_fortfloat('A', txt)
            # Check that not both were specified
            if celldm1 and a:
                raise InputValidationError('Both A and celldm(1) specified')
            if a:
                conversion = a
            elif celldm1:
                conversion = bohr_to_ang * celldm1
            else:
                raise InputValidationError(
                    'You have to define lattice vector'
                    'celldm(1) or A'
                )
        cell = conversion * cell

    # Ok, user was not nice and used ibrav > 0 to define cell using
    # either the keys celldm(n) n = 1,2,...,6  (celldm - system)
    # or A,B,C, cosAB, cosAC, cosBC (ABC-system)
    # to define the necessary cell geometry factors
    else:
        # The user should define exclusively in celldm or ABC-system
        # NOT both
        # I am only going to this for the important first lattice vector
        celldm1 = get_fortfloat('celldm\(1\)', txt)
        a = get_fortfloat('A', txt)
        if celldm1 and a:
            raise InputValidationError(
                'Both A and celldm(1) specified'
            )
        elif not (celldm1 or a):
            raise Exception('You have to define lattice vector'
                            'celldm(1) or A'
                            )
        # So, depending on what is defined for the first lattice vector,
        # I define the keys that I will look for to find the other
        # geometry definitions
        try:
            if celldm1:
                keys_in_qeinput = (
                    'celldm\(2\)',
                    'celldm\(3\)',
                    'celldm\(4\)',
                    'celldm\(5\)',
                    'celldm\(6\)',
                )
                # I will do all my calculations in ABC-system and
                # therefore need a conversion factor
                # if celldm system is chosen:
                a = bohr_to_ang * celldm1
                length_conversion = a
            else:
                keys_in_qeinput = (
                    'B',
                    'C',
                    'cosAB',
                    'cosAC',
                    'cosBC',
                )
                length_conversion = 1.
            # Not all geometry definitions are needs,
            # but some are necessary depending on ibrav
            # and will be matched here:
            if abs(ibrav) > 7:
                i = 0
                b = length_conversion * get_fortfloat(keys_in_qeinput[i], txt)
            if abs(ibrav) > 3 and ibrav not in (-5, 5):
                i = 1
                c = length_conversion * get_fortfloat(keys_in_qeinput[i], txt)
            if ibrav in (12, 13, 14):
                i = 2
                cosg = get_fortfloat(keys_in_qeinput[i], txt)
                sing = np.sqrt(1. - cosg ** 2)
            if ibrav in (-12, 14):
                i = 3
                cosb = get_fortfloat(keys_in_qeinput[i], txt)
                sinb = np.sqrt(1. - cosb ** 2)
            if ibrav in (5, 14):
                i = 4
                cosa = 1. * get_fortfloat(keys_in_qeinput[i], txt)
                # The multiplication with 1.
                # raises Exception here if None was returned by get_fortfloat
        except Exception as e:
            raise InputValidationError(
                '\nException {} raised when searching for\n'
                'key {} in qeinput, necessary when ibrav = {}'.format(
                    e, keys_in_qeinput[i], ibrav
                )
            )
    # Calculating the cell according to ibrav.
    # The comments in each case are taken from
    # http://www.quantum-espresso.org/wp-content/uploads/Doc/INPUT_PW.html#ibrav
    if ibrav == 1:
        # 1          cubic P (sc)
        # v1 = a(1,0,0),  v2 = a(0,1,0),  v3 = a(0,0,1)
        cell = np.diag([a, a, a])
    elif ibrav == 2:
        #  2          cubic F (fcc)
        #  v1 = (a/2)(-1,0,1),  v2 = (a/2)(0,1,1), v3 = (a/2)(-1,1,0)
        cell = 0.5 * a * np.array([
            [-1., 0., 1.],
            [0., 1., 1.],
            [-1., 1., 0.],
        ])
    elif ibrav == 3:
        # cubic I (bcc)
        #  v1 = (a/2)(1,1,1),  v2 = (a/2)(-1,1,1),  v3 = (a/2)(-1,-1,1)
        cell = 0.5 * a * np.array([
            [1., 1., 1.],
            [-1., 1., 1.],
            [-1., -1., 0.],
        ])
    elif ibrav == 4:
        # 4          Hexagonal and Trigonal P        celldm(3)=c/a
        # v1 = a(1,0,0),  v2 = a(-1/2,sqrt(3)/2,0),  v3 = a(0,0,c/a)
        cell = a * np.array([
            [1., 0., 0.],
            [-0.5, 0.5 * np.sqrt(3.), 0.],
            [0., 0., c / a]
        ])
    elif ibrav == 5:
        # 5          Trigonal R, 3fold axis c        celldm(4)=cos(alpha)
        # The crystallographic vectors form a three-fold star around
        # the z-axis, the primitive cell is a simple rhombohedron:
        # v1 = a(tx,-ty,tz),   v2 = a(0,2ty,tz),   v3 = a(-tx,-ty,tz)
        # where c=cos(alpha) is the cosine of the angle alpha between
        # any pair of crystallographic vectors, tx, ty, tz are:
        # tx=sqrt((1-c)/2), ty=sqrt((1-c)/6), tz=sqrt((1+2c)/3)
        tx = np.sqrt((1. - cosa) / 2.)
        ty = np.sqrt((1. - cosa) / 6.)
        tz = np.sqrt((1. + 2. * cosa) / 3.)
        cell = a * np.array([
            [tx, -ty, tz],
            [0., 2 * ty, tz],
            [-tx, -ty, tz]
        ])
    elif ibrav == -5:
        # -5          Trigonal R, 3fold axis <111>    celldm(4)=cos(alpha)
        # The crystallographic vectors form a three-fold star around
        # <111>. Defining a' = a/sqrt(3) :
        # v1 = a' (u,v,v),   v2 = a' (v,u,v),   v3 = a' (v,v,u)
        # where u and v are defined as
        # u = tz - 2*sqrt(2)*ty,  v = tz + sqrt(2)*ty
        # and tx, ty, tz as for case ibrav=5
        # Note: if you prefer x,y,z as axis in the cubic limit,
        # set  u = tz + 2*sqrt(2)*ty,  v = tz - sqrt(2)*ty
        # See also the note in flib/latgen.f90
        tx = np.sqrt((1. - c) / 2.)
        ty = np.sqrt((1. - c) / 6.)
        tz = np.sqrt((1. + 2. * c) / 3.)
        u = tz - 2. * np.sqrt(2.) * ty
        v = tz + np.sqrt(2.) * ty
        cell = a / np.sqrt(3.) * np.array([
            [u, v, v],
            [v, u, v],
            [v, v, u]
        ])
    elif ibrav == 6:
        # 6          Tetragonal P (st)               celldm(3)=c/a
        # v1 = a(1,0,0),  v2 = a(0,1,0),  v3 = a(0,0,c/a)
        cell = a * np.array([
            [1., 0., 0.],
            [0., 1., 0.],
            [0., 0., c / a]
        ])
    elif ibrav == 7:
        # 7          Tetragonal I (bct)              celldm(3)=c/a
        # v1=(a/2)(1,-1,c/a),  v2=(a/2)(1,1,c/a),  v3=(a/2)(-1,-1,c/a)
        cell = 0.5 * a * np.array([
            [1., -1., c / a],
            [1., 1., c / a],
            [-1., -1., c / a]
        ])
    elif ibrav == 8:
        # 8  Orthorhombic P       celldm(2)=b/a
        #                         celldm(3)=c/a
        #  v1 = (a,0,0),  v2 = (0,b,0), v3 = (0,0,c)
        cell = np.diag([a, b, c])
    elif ibrav == 9:
        #   9   Orthorhombic base-centered(bco) celldm(2)=b/a
        #                                         celldm(3)=c/a
        #  v1 = (a/2, b/2,0),  v2 = (-a/2,b/2,0),  v3 = (0,0,c)
        cell = np.array([
            [0.5 * a, 0.5 * b, 0.],
            [-0.5 * a, 0.5 * b, 0.],
            [0., 0., c]
        ])
    elif ibrav == -9:
        # -9          as 9, alternate description
        #  v1 = (a/2,-b/2,0),  v2 = (a/2,-b/2,0),  v3 = (0,0,c)
        cell = np.array([
            [0.5 * a, 0.5 * b, 0.],
            [0.5 * a, -0.5 * b, 0.],
            [0., 0., c]
        ])
    elif ibrav == 10:
        # 10          Orthorhombic face-centered      celldm(2)=b/a
        #                                         celldm(3)=c/a
        #  v1 = (a/2,0,c/2),  v2 = (a/2,b/2,0),  v3 = (0,b/2,c/2)
        cell = np.array([
            [0.5 * a, 0., 0.5 * c],
            [0.5 * a, 0.5 * b, 0.],
            [0., 0.5 * b, 0.5 * c]
        ])
    elif ibrav == 11:
        # 11          Orthorhombic body-centered      celldm(2)=b/a
        #                                        celldm(3)=c/a
        #  v1=(a/2,b/2,c/2),  v2=(-a/2,b/2,c/2),  v3=(-a/2,-b/2,c/2)
        cell = np.array([
            [0.5 * a, 0.5 * b, 0.5 * c],
            [-0.5 * a, 0.5 * b, 0.5 * c],
            [-0.5 * a, -0.5 * b, 0.5 * c]
        ])
    elif ibrav == 12:
        # 12      Monoclinic P, unique axis c     celldm(2)=b/a
        #                                         celldm(3)=c/a,
        #                                         celldm(4)=cos(ab)
        #  v1=(a,0,0), v2=(b*cos(gamma),b*sin(gamma),0),  v3 = (0,0,c)
        #  where gamma is the angle between axis a and b.
        cell = np.array([
            [a, 0., 0.],
            [b * cosg, b * sing, 0.],
            [0., 0., c]
        ])
    elif ibrav == -12:
        # -12          Monoclinic P, unique axis b     celldm(2)=b/a
        #                                         celldm(3)=c/a,
        #                                         celldm(5)=cos(ac)
        #  v1 = (a,0,0), v2 = (0,b,0), v3 = (c*cos(beta),0,c*sin(beta))
        #  where beta is the angle between axis a and c
        cell = np.array([
            [a, 0., 0.],
            [0., b, 0.],
            [c * cosb, 0., c * sinb]
        ])
    elif ibrav == 13:
        # 13          Monoclinic base-centered        celldm(2)=b/a
        #                                          celldm(3)=c/a,
        #                                          celldm(4)=cos(ab)
        #  v1 = (  a/2,         0,                -c/2),
        #  v2 = (b*cos(gamma), b*sin(gamma), 0),
        #  v3 = (  a/2,         0,                  c/2),
        #  where gamma is the angle between axis a and b
        cell = np.array([
            [0.5 * a, 0., -0.5 * c],
            [b * cosg, b * sing, 0.],
            [0.5 * a, 0., 0.5 * c]
        ])
    elif ibrav == 14:
        #  14       Triclinic                     celldm(2)= b/a,
        #                                         celldm(3)= c/a,
        #                                         celldm(4)= cos(bc),
        #                                         celldm(5)= cos(ac),
        #                                         celldm(6)= cos(ab)
        #  v1 = (a, 0, 0),
        #  v2 = (b*cos(gamma), b*sin(gamma), 0)
        #  v3 = (c*cos(beta),  c*(cos(alpha)-cos(beta)cos(gamma))/sin(gamma),
        #       c*sqrt( 1 + 2*cos(alpha)cos(beta)cos(gamma)
        #                 - cos(alpha)^2-cos(beta)^2-cos(gamma)^2 )/sin(gamma) )
        # where alpha is the angle between axis b and c
        #     beta is the angle between axis a and c
        #    gamma is the angle between axis a and b
        cell = np.array([
            [a, 0., -0.5 * c],
            [b * cosg, b * sing, 0.],
            [
                c * cosb,
                c * (cosa - cosb * cosg) / sing,
                c * np.sqrt(
                    1. + 2. * cosa * cosb * cosg - cosa ** 2 - cosb ** 2 - cosg ** 2) / sing
            ]
        ])

    # Ok, I have a valid cell (numpy)
    

    #################  KINDS ##########################

    atomic_species = atomic_species_block_regex.search(txt).group('block')
    for match in atomic_species_regex.finditer(atomic_species):
        try:
            symbols = valid_elements_regex.search(
                match.group('pseudo')
            ).group('ele')
        except Exception as e:
            raise InputValidationError(
                'I could not read an element name in {}'.format(match.group(0))
            )
        name = match.group('tag')
        mass = match.group('mass')

    ################## POSITIONS #######################

    atom_block_match = pos_block_regex.search(txt)
    valid_atom_units = ('alat', 'bohr', 'angstrom', 'crystal', 'crystal_sg')
    atom_unit = atom_block_match.group('units') or 'alat'
    atom_unit = atom_unit.lower()

    if atom_unit not in valid_atom_units:
        raise InputValidationError(
            '\nFound atom unit {}, which is not\n'
            'among the valid units: {}'.format(
                atom_unit, ', '.join(valid_atom_units)
            )
        )

    if atom_unit == 'crystal_sg':
        raise NotImplementedError('crystal_sg is not implemented')
    position_block = atom_block_match.group('positions')

    if not position_block:
        raise InputValidationError('Could not read CARD POSITIONS')

    symbols, positions = [], []

    for atom_match in pos_regex.finditer(position_block):
        symbols.append(atom_match.group('sym'))
        try:
            positions.append(
                [
                    float(
                        atom_match.group(c).replace('D', 'e').replace('d', 'e'))
                    for c in ('x', 'y', 'z')
                    ]
            )
        except Exception as e:
            raise InputValidationError(
                'I could not get position in\n'
                '{}\n'
                '({})'.format(atom_match.group(0), e)
            )
    positions = np.array(positions)

    if atom_unit == 'bohr':
        positions = bohr_to_ang * positions
    elif atom_unit == 'crystal':
        positions = np.dot(positions, cell)
    elif atom_unit == 'alat':
        positions = np.linalg.norm(cell[0]) * positions

    ######### DEFINE SITES ######################

    #absolute_positions
    positions = positions.tolist()
    # rel positions
    rel_position = np.dot(positions, np.linalg.inv(cell))

    try:
        numbers = [atoms_num_dict[sym] for sym in symbols]
    except KeyError as e:
        raise InputValidationError("Unknown symbol '{}'".format(
            e.message))

    return (cell.tolist(), rel_position.tolist(), numbers)
