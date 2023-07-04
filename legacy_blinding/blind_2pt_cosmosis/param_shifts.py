import hashlib
import numpy as np
import importlib

DEFAULT_PARAM_RANGE = {'cosmological_parameters--sigma8_input':(0.834-3*.04,0.834+3*0.04),\
                       'cosmological_parameters--w':(-1.5,-.5)}

def draw_param_shift(seedstring='blinded', ranges=None, importfrom=None):
    """
    Given a string seed, pseudo-randomly draws shift in parameter space.

    By default, draws random values for all the parameters with ranges defined
    in the dictionary 'ranges'. Note:
      - parameter names should match those used by cosmosis (see
        DEFAULT_PARAM_RANGE dict for an example)
      - ranges is a dictionary with parameter names as keys, the values are
        tuples set up as (min,max). The parameter will be drawn from a flat
        distribution between min and max.

    importfrom:
    If you'd like to draw from a different distribution, create another .py
    file with an function in it called draw_paramshift, making sure it return
    a dictuionary with the same format as below:
      - If you pass a string with that file's name as an argument importfrom,
        that distribution will be used instead of this one.
      - The returned dictionary will be expected to have key 'SHIFTS' associated
        with a bool to determine how the values in that dictionary are used.
           pdict['SHIFTS'] = False --> p_shift = pdict['paramname']
           pdict['SHIFTS'] = True  --> p_shift = p_ref + pdict['paramname']

    Make sure any parameters that are shifted here have names matching
    how cosmosis uses them, so that the code in the for loop starting with
    'for parameter in pipeline.parameters' in run_cosmosis_togen_2ptdict
    will work.
    """
    # sets the seed:
    seedind = int(int(hashlib.md5(seedstring.encode('utf-8')).hexdigest(), 16) % 1.e8)
    np.random.seed(seedind)

    if importfrom is None:
        # sorting makes sure it's always the same order
        params2shift = sorted(ranges.keys())
        Nparam = len(params2shift)
        # arrays between 0 and 1
        shiftfrac = np.random.rand(Nparam)
        mins, maxs = zip(*[ranges[k] for k in params2shift])
        dparams = np.array(mins) + (np.array(maxs) - np.array(mins)) * shiftfrac
        pdict = {param: value for param, value in zip(params2shift, dparams)}
        pdict['SHIFTS'] = False
    else:
        paramdraw = importlib.import_module(importfrom)
        pdict = paramdraw.draw_paramshift()

        if 'SHIFTS' not in pdict:
            raise ValueError("Can't find key 'SHIFTS' in pdict." +
                             "Set to True if the dict contains Delta params," +
                             " False if it contains param values.")
    return pdict
