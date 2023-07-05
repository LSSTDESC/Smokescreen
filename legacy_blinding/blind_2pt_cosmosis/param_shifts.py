import hashlib
import numpy as np
from .io import DEFAULT_PARAM_RANGE

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
