# author: Arthur Loureiro <arthur.loureiro@fysik.su.se>
# license: BSD 3-Clause
'''
Parameter Shifts (:mod:`smokescreen.param_shifts`)
===================================================

.. currentmodule:: smokescreen.param_shifts

The :mod:`smokescreen.param_shifts` module provides modules
to perform shifts in the cosmological parameters.


Parameter Shifts
-----------------

.. autofunction:: draw_flat_param_shifts
.. autofunction:: draw_flat_or_deterministic_param_shifts
.. autofunction:: draw_gaussian_param_shifts
'''
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
        Dictionary of parameter names and corresponding shift. If the
        shifts are single values, it does a deterministic shift: PARAM = FIDUCIAL + SHIFT
        If the shifts are tuples of values, the dictionary values
        should be the (lower, upper) bounds of the shift widths: PARAM = U(a, b)
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

    # check if the keys in the shifts_dict are in the cosmology parameters
    for key in shifts_dict.keys():
        try:
            cosmo._params[key]
        except (AttributeError, KeyError) as error:
            # remove the key from the shifts_dict
            # print(f"Key {key} not in cosmology parameters")
            # failed_keys.append(key)
            raise ValueError(f"[{error}]Key {key} not in cosmology parameters")
    shifts = {}
    # we loop over the ccl dict keys to ensure params are drawn in the same order!
    for key in cosmo.to_dict().keys():
        if key in shifts_dict.keys():
            if isinstance(shifts_dict[key], tuple):
                # check if the tuple is of length 2
                if len(shifts_dict[key]) == 2:
                    shifts[key] = np.random.uniform(shifts_dict[key][0], shifts_dict[key][1])
                else:
                    raise ValueError(f"Tuple {shifts_dict[key]} has to be of length 2")
            else:
                shifts[key] = shifts_dict[key]
        else:
            pass
    return shifts


def draw_gaussian_param_shifts(cosmo, shifts_dict, seed):
    """
    Draw Gaussian parameter shifts from a dictionary of parameter names and
    corresponding shift widths.

    Parameters
    ----------
    cosmo : pyccl.Cosmology
        Cosmology object.
    shift_dict : dict
        Dictionary of parameter names and corresponding shift widths. The
        dictionary values should be the (mean, std) of the Gaussian distribution.
    seed : int or str
        Random seed.

    Returns
    -------
    shifts : dict
        Dictionary of parameter names and corresponding Gaussian parameter shifts.
    """
    if type(seed) is str:
        seed = string_to_seed(seed)
    np.random.seed(seed)
    for key in shifts_dict.keys():
        try:
            cosmo._params[key]
        except (AttributeError, KeyError) as error:
            # remove the key from the shifts_dict
            # print(f"Key {key} not in cosmology parameters")
            # failed_keys.append(key)
            raise ValueError(f"[{error}]Key {key} not in cosmology parameters")
    shifts = {}
    # we loop over the ccl dict keys to ensure params are drawn in the same order!
    for key in cosmo.to_dict().keys():
        if key in shifts_dict.keys():
            if isinstance(shifts_dict[key], tuple):
                # check if the tuple is of length 2
                if len(shifts_dict[key]) == 2:
                    shifts[key] = np.random.normal(shifts_dict[key][0], shifts_dict[key][1])
                else:
                    raise ValueError(f"Tuple {shifts_dict[key]} has to be of length 2")
            else:
                raise ValueError(f"Value {shifts_dict[key]} has to be a tuple of length 2")
        else:
            pass
    return shifts
