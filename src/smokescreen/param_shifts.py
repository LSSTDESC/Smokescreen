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
    if type(seed) is str:
        seed = string_to_seed(seed)
    np.random.seed(seed)
    # check the if the shifts are single value or a tuple of values
    if type(list(shift_dict.values())[0]) is tuple:
        return {par: np.random.uniform(shift_dict[par][0], shift_dict[par][1])
                for par in shift_dict}
    else:
        return {par: np.random.uniform(-shift_dict[par], shift_dict[par])
                for par in shift_dict}


def draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed):
    """
    Draw flat or deterministic parameter shifts from a dictionary of parameter
    names and corresponding shift widths.

    Parameters
    ----------
    cosmo : pyccl.Cosmology
        Cosmology object.
    shift_dict : dict
        Dictionary of parameter names and corresponding shift widths. If the
        shifts are single values, it does a deterministic shift: PARAM = FIDUCIAL + SHIFT
        If the shifts are tuples of values, the dictionary values
        should be the (lower, upper) bounds of the shift widths: PARAM = U(a, b)
        If the first valuee is negative, it is assumed that the parameter
        is to be shifted from the fiducial value: PARAM = FIDUCIAL + U(-a, b)
    seed : int or str
        Random seed.

    Returns
    -------
    dict
        Dictionary of parameter names and corresponding flat or deterministic
        parameter shifts.
    """
    if type(seed) is str:
        seed = string_to_seed(seed)
    np.random.seed(seed)
    # check the if the shifts are single value or a tuple of values
    for key in shifts_dict.keys():
        try:
            cosmo._params[key]
        except (AttributeError, KeyError) as error:
            # remove the key from the shifts_dict
            # print(f"Key {key} not in cosmology parameters")
            # failed_keys.append(key)
            raise ValueError(f"[{error}]Key {key} not in cosmology parameters")
    shifts = {}
    for key, value in shifts_dict.items():
        if isinstance(value, tuple):
            # check if the tuple is of length 2
            if len(value) == 2:
                if value[0] < 0:
                    shifts[key] = cosmo[key] + np.random.uniform(value[0], value[1])
                else:
                    shifts[key] = np.random.uniform(value[0], value[1])
            else:
                raise ValueError(f"Tuple {value} has to be of length 2")
        else:
            shifts[key] = value
    return shifts
