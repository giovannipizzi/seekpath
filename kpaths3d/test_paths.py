import hkot

def test_case(case, with_inv):
    import os
    import ase, ase.io

    # Get the POSCAR with the example structure
    this_folder = os.path.split(os.path.abspath(hkot.__file__))[0]
    folder = os.path.join(this_folder,"band_path_data",case)
    poscar_with_inv = os.path.join(folder,'POSCAR_inversion')
    poscar_no_inv = os.path.join(folder,'POSCAR_noinversion')

    poscar = poscar_with_inv if with_inv else poscar_no_inv
    asecell = ase.io.read(poscar)
    # With time reversal set to False to get the most complete path
    try:
        res = hkot.get_path(asecell, with_time_reversal=False) 

        if res['bravais_lattice_case'] != case:
            raise AssertionError("bravais_lattice_case: expected {} "
                "but detected {}".format(case, res['bravais_lattice_case']))
        if res['has_inversion_symmetry'] != with_inv:
            raise AssertionError("inversion_symmetry: expected {} "
                "but detected {}".format(with_inv, res['has_inversion_symmetry']))

        print "*** {} (inv={})".format(
            case, with_inv)
        for p1, p2 in res['path']:
            print "   {} -- {}: {} -- {}".format(p1, p2, 
                res['point_coords'][p1], res['point_coords'][p2])
    except NotImplementedError:
        print "*** {} (inv={}): {}".format(case, with_inv, "NOT IMPLEMENTED")

if __name__ == "__main__":

    for case in ['aP2', 'aP3', 'cF1', 'cF2', 'cI1', 'cP1', 'cP2', 'hP1', 'hP2', 
            'hR1', 'hR2', 'mC1', 'mC2', 'mC3', 'mP1', 'oA1', 'oA2', 
            'oC1', 'oC2', 'oF1', 'oF2', 'oF3', 'oI1', 'oI2', 'oI3', 
            'oP1', 'tI1', 'tI2', 'tP1']:
        # oF2Y does not exist for symmetry reasons
        if case not in ['oF2', 'oA1', 'oA2']:
            test_case(case, with_inv = True)
        test_case(case, with_inv = False)

    # import ase
    # # spgrp 12, mC, invsym: [12, 15]
    # #b > a * sqrt(1-cosbeta**2)
    # #-a * cosbeta / c + a**2 * (1 - cosbeta**2) / b**2 > 1

    # s = ase.Atoms('C2O8', cell=[[3,0,0],[0,2,0],[-1,0,0.8]])
    # s.set_scaled_positions(
    #     [
    #         [0,0,0],
    #         [0.5,0.5,0],
    #         [0.1,0.2,0.3],
    #         [-0.1,0.2,-0.3],
    #         [-0.1,-0.2,-0.3],
    #         [0.1,-0.2,0.3],
    #         [0.6,0.7,0.3],
    #         [-0.6,0.7,-0.3],
    #         [-0.6,-0.7,-0.3],
    #         [0.6,-0.7,0.3],
    #     ])
    # print get_path(s)
