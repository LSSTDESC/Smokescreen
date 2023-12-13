import numpy as np
from .utils import string_to_seed

def draw_flat_param_shifts(shift_dict, seed):
    """
    Draw flat parameter shifts from a dictionary of parameter names and
    corresponding shift widths.

    Parameters
    ----------
    shift_dict : dict
        Dictionary of parameter names and corresponding shift widths. If the
        shifts are single values, the dictionary values should be the shift
        widths. If the shifts are tuples of values, the dictionary values
        should be the (lower, upper) bounds of the shift widths.
    seed : int or str
        Random seed.

    Returns
    -------
    dict
        Dictionary of parameter names and corresponding flat parameter shifts.
    """
    if type(seed) == str:
        seed = string_to_seed(seed)
    np.random.seed(seed)
    # check the if the shifts are single value or a tuple of values
    if type(list(shift_dict.values())[0]) == tuple:
        return {par: np.random.uniform(shift_dict[par][0], shift_dict[par][1])
            for par in shift_dict}
    else:
        return {par: np.random.uniform(-shift_dict[par], shift_dict[par])
                for par in shift_dict}