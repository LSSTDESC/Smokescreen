import numpy as np
import os
import sys
import importlib
import logging
logger = logging.getLogger("2pt_blinding")


# gambiarra to import cosmosis modules
CSD = os.environ['COSMOSIS_SRC_DIR']+'/cosmosis-standard-library/likelihood/2pt/'
TWOPT_MODULE = "twopoint_cosmosis"
sys.path.insert(0, CSD)
twopoint_cosmosis = importlib.import_module(TWOPT_MODULE)
from twopoint_cosmosis import type_table

def spectrum_array_from_block(block, section_name, types, xlabel='theta', bin_format='bin_{0}_{1}'):
    is_auto = (types[0] == types[1])
    nbin_a = block[section_name, "nbin"] if block.has_value(section_name, "nbin") else block[section_name, "nbin_a"]
    nbin_b = nbin_a if is_auto else block[section_name, "nbin_b"]

    theory_angle = block[section_name, xlabel]
    n_angle = len(theory_angle)
    is_binavg = block[section_name, "bin_avg"]

    if is_binavg:
        theory_angle_edges = block[section_name, xlabel + '_edges']

    value = []
    bin1 = []
    bin2 = []
    angles = []
    angle_mins = []
    angle_maxs = [] if is_binavg else None

    for i in range(nbin_a):
        jmax = i + 1 if is_auto else nbin_b
        for j in range(jmax):
            binlabel = bin_format.format(i + 1, j + 1)
            if block.has_value(section_name, binlabel):
                cl = block[section_name, binlabel]
                bin1.extend([i + 1] * n_angle)
                bin2.extend([j + 1] * n_angle)
                angles.extend(theory_angle)
                if is_binavg:
                    angle_mins.extend(theory_angle_edges[:-1])
                    angle_maxs.extend(theory_angle_edges[1:])
                value.extend(cl)
                if is_auto and i != j:
                    bin1.extend([j + 1] * n_angle)
                    bin2.extend([i + 1] * n_angle)
                    value.extend(cl)
                    angles.extend(theory_angle)
                    if is_binavg:
                        angle_mins.extend(theory_angle_edges[:-1])
                        angle_maxs.extend(theory_angle_edges[1:])

    value = np.array(value)
    bin1 = np.array(bin1)
    bin2 = np.array(bin2)
    bins = (bin1, bin2)
    angles = np.array(angles)
    angle_mins = np.array(angle_mins) if is_binavg else None
    angle_maxs = np.array(angle_maxs) if is_binavg else None

    return angles, value, bins, is_binavg, angle_mins, angle_maxs

def get_dictkey_for_2pttype(type1, type2):
    """
    Convert strings used in fits file to label spectra type in fits file to
    dictionary keys expected by this script's functions.
    (fits file 2pt table naming -> this script's naming)
    """
    logger.debug("Requested: \n\ttype1: {0:s}, type2: {1:s}".format(type1, type2))
    mapping = {
        'G': 'galaxy',
        'C': 'cmb',
        'P': 'position',
        'E': 'shear_emode',
        'B': 'shear_bmode',
        '+': 'shear_plus',
        '-': 'shear_minus',
        'K': 'kappa',
        'R': 'real',
        'F': 'fourier'
    }

    if type1 in ("GPF", "GEF", "GBF", "GPR", "G+R", "G-R", "CKR", "GPF", "GEF", "GBF"):
        # Translate short codes into longer strings
        newtypes = ['_'.join([mapping[t[0]], mapping[t[1]], mapping[t[2]]]) for t in [type1, type2]]
        type1 = newtypes[0]
        type2 = newtypes[1]

    try:
        section, xlabel, ylabel = type_table[(type1, type2)]
        ykey = section
        xkey = f"{section}_{xlabel}"
    except KeyError:
        raise ValueError("Spectra type not recognized: {0:s}, {1:s} ".format(type1, type2))

    return xkey, ykey
