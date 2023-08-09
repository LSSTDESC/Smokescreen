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

def spectrum_array_from_block(block, section_name, types, xlabel='theta', bin_format = 'bin_{0}_{1}'):
    """
    >> Updated 4/21/20 to work with bin averaging implemented for DES Y3
    
    Initially adapting this from save_2pt.py and 2pt_like code.

    No scale cutting implemented or angular sampling;
    that will be handled later. Since we
    track bin numbers and angle values, which will be checked against
    the unblinded fits file in get_dictdat_tomatch_fitsdat.
    """
    if xlabel=='theta':
        is_binavg = block[section_name,"bin_avg"]
    else:
        is_binavg = False #no bin averaging in fourier space

    # for cross correlations we must save bin_ji as well as bin_ij.
    # but not for auto-correlations.
    is_auto = (types[0] == types[1])
    if block.has_value(section_name, "nbin"):
        nbin_a = block[section_name, "nbin"]
    else:
        nbin_a = block[section_name, "nbin_a"]
        nbin_b = block[section_name, "nbin_b"]


    #This is the ell/theta values that have been calculated by cosmosis,
    # if bin averaging, these should match what's in the fits files (up to rounding)
    # if interpolating, angles will be more densely sampled than values in fits files.
    theory_angle = block[section_name,xlabel]
    n_angle = len(theory_angle) #whatevers in the block, length of array
    if is_binavg:
        theory_angle_edges = block[section_name,xlabel+'_edges'] #angle bin edges

    #The fits format stores all the measurements
    #as one long vector.  So we build that up here from the various
    #bins that we will load in.  These are the different columns
    value = []
    bin1 = []
    bin2 = []
    angles = []
    # these will only be used if averaging over angular bins
    angle_mins = []
    angle_maxs = []

    # n.b. don't have suffix option implemented here

    #Bin pairs. Varies depending on auto-correlation
    for i in range(nbin_a):
        if is_auto:
            jmax = i+1
        else:
            jmax = nbin_b
        for j in range(jmax):
            #Load and interpolate from the block
            binlabel = bin_format.format(i+1,j+1)
            if block.has_value(section_name, binlabel):
                cl = block[section_name, binlabel]
                bin1.append(np.repeat(i + 1, n_angle))
                bin2.append(np.repeat(j + 1, n_angle))
                angles.append(theory_angle)
                if is_binavg:
                    angle_mins.append(theory_angle_edges[:-1])
                    angle_maxs.append(theory_angle_edges[1:])
                value.append(cl)

                if is_auto and i!=j: #also store under flipped z bin labels
                    # this allows the script to work w fits files uing either convention
                    bin1.append(np.repeat(j + 1, n_angle))
                    bin2.append(np.repeat(i + 1, n_angle))
                    value.append(cl)
                    angles.append(theory_angle)
                    if is_binavg:
                        angle_mins.append(theory_angle_edges[:-1])
                        angle_maxs.append(theory_angle_edges[1:])
                    

    #Convert all the lists of vectors into long single vectors
    value = np.concatenate(value)
    bin1 = np.concatenate(bin1)
    bin2 = np.concatenate(bin2)
    bins = (bin1,bin2)
    angles = np.concatenate(angles)
    if is_binavg:
        angle_mins = np.concatenate(angle_mins)
        angle_maxs = np.concatenate(angle_maxs)
    else:
        angle_mins = None
        angle_maxs = None

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
    logger.debug("Returning: \n\txkey: {0:s}, ykey: {1:s}".format(xkey, ykey))
    return xkey, ykey

def get_twoptdict_from_pipeline_data(data):
    """
    Extract 2pt data from a cosmosis pipeline data object and return a dictionary
    with keys corresponding to the 2pt spectra types.

    For auto spectra where z bin label order doesn't matter, both orders
    will be stored. (e.g. the same data will be there for bins 1-2 and 2-1).
    """
    outdict = {}
    type_keys = [types for types in type_table if data.has_section(type_table[types][0])]

    for types in type_keys:
        section, xlabel, binformat = type_table[types]
        xkey, ykey = get_dictkey_for_2pttype(types[0], types[1])
        
        x, y, bins, is_binavg, x_mins, x_maxs = spectrum_array_from_block(data, section, types, xlabel, binformat)
        
        outdict[xkey] = x
        outdict[ykey] = y
        outdict[ykey + '_bins'] = bins
        outdict[ykey + '_binavg'] = is_binavg
        
        if is_binavg:
            outdict[xkey + '_mins'] = x_mins
            outdict[xkey + '_maxs'] = x_maxs
    
    return outdict