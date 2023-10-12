import hashlib
import logging
import numpy as np
from .io import DEFAULT_PARAM_RANGE

logger = logging.getLogger("2pt_blinding")

def draw_flat_param_shift(seedstring='blinded', ranges=None):
    """
    Given a string seed, pseudo-randomly draws shift in parameter space.

    By default, draws random values for all the parameters with ranges defined
    in the dictionary 'ranges'. Note:
      - parameter names should match those used by cosmosis (see
        DEFAULT_PARAM_RANGE dict for an example)
      - ranges is a dictionary with parameter names as keys, the values are
        tuples set up as (min,max). The parameter will be drawn from a flat
        distribution between min and max.

    Make sure any parameters that are shifted here have names matching
    how cosmosis uses them, so that the code in the for loop starting with
    'for parameter in pipeline.parameters' in run_cosmosis_togen_2ptdict
    will work.
    """
    # sets the seed:
    seedind = int(int(hashlib.md5(seedstring.encode('utf-8')).hexdigest(), 16) % 1.e8)
    np.random.seed(seedind)

    if ranges is None:
        ranges = DEFAULT_PARAM_RANGE

    # sorting makes sure it's always the same order
    params2shift = sorted(ranges.keys())
    Nparam = len(params2shift)
    # arrays between 0 and 1
    shiftfrac = np.random.rand(Nparam)
    mins, maxs = zip(*[ranges[k] for k in params2shift])
    dparams = np.array(mins) + (np.array(maxs) - np.array(mins)) * shiftfrac
    pdict = {param: value for param, value in zip(params2shift, dparams)}
    pdict['SHIFTS'] = False

    return pdict

def apply_parameter_shifts(pipeline, pdict):
    """
    Apply parameter shifts to the pipeline parameters.
    """
    doshifts = len(list(pdict.keys()))
    if doshifts > 0:
        SHIFTS = pdict['SHIFTS']
        haveshifted = []
        # set parameters as desired
    for parameter in pipeline.parameters:
        key = str(parameter)
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>......", key)
        #set the values
        if doshifts > 0:
            try:
                if SHIFTS:
                    logger.debug(f"Shifting parameter {key} by {pdict[key]}")
                    parameter.start = parameter.start + pdict[key]
                    logger.debug(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>...... {parameter.start}")
                else:
                    logger.debug(f"Shifting parameter {key} to {pdict[key]}")
                    parameter.start = pdict[key]
                    logger.debug(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>...... {parameter.start}")
                haveshifted.append(key)
            except KeyError:
                print("  asked for shifts in:", key)
                logger.debug(f"Parameter {key} not in pdict. Not shifting.")
                pass

    if (doshifts > 0) and (len(haveshifted) != (len(list(pdict.keys())) -1)):
        print("  asked for shifts in:",list(pdict.keys()))
        print("  did shifts in:",haveshifted)
        raise ValueError("WARNING: YOU ASKED FOR SHIFTS IN PARAMTERS NOT IN THE COSMOSIS PIPELINE.")
    return pipeline

def get_factordict(refdict,shiftdict,bftype='add'):
    """
    Given two point dictionaries for reference and shifted cosmology,
    returns dictionary of blinding factors.

    Parameters
    ----------
    refdict : dict
        Dictionary of reference cosmology 2pt functions.
    shiftdict : dict
        Dictionary of shifted cosmology 2pt functions.
    bftype : str, optional
        What kind of blinding factor is it?
        'add' : bf = - ref + shift
        'mult': bf = shift/ref
        'multNOCS': bf = shift/ref, but with no cosmic shear
            (i.e. no E-mode or B-mode shear)
        Default is 'add'.

    Returns
    -------
    factordict : dict
        Dictionary of blinding factors.
    """

    factordict = {}
    for key in refdict:
        end = key[key.rfind('_')+1:]
        #print(key,end)
        # don't take ratios or differences of angle/multipole info
        if end in ['ell','l','theta','bins','angbins','binavg','mins','maxs']:
            #print '    no change'
            factordict[key] = refdict[key]
        else:
            if bftype=='mult' or bftype=='multNOCS':
                logger.debug('    dividing!')
                factordict[key] = shiftdict[key]/refdict[key]
            elif bftype=='add':
                logger.debug('    adding!')
                factordict[key] = shiftdict[key] - refdict[key]
            else:
                raise ValueError('In get_factordict: blinding factor type not recognized')
    return factordict