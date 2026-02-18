# author: Arthur Loureiro <arthur.loureiro@fysik.su.se>
# license: BSD 3-Clause
'''
Utils (:mod:`smokescreen.utils`)
===================================================

.. currentmodule:: smokescreen.utils

The :mod:`smokescreen.utils` module provides utility functions
for the smokescreen package.


Smokescreen Utils
-----------------

.. autofunction:: load_cosmology_from_partial_dict
.. autofunction:: load_module_from_path
.. autofunction:: string_to_seed
'''
import hashlib
import importlib.util
import pyccl as ccl


def load_cosmology_from_partial_dict(cosmo_dict):
    """
    Given a partial dictionary with cosmological parameters, return a Cosmology
    object setting the unspecified parameters to their default values.

    Parameters
    ----------
    cosmo_dict : dict
        Dictionary with the cosmological parameters.

    Returns
    -------
    Cosmology
        Cosmology object with the specified parameters.
    """
    # sets the default values for the cosmological parameters
    cosmo_dict_default = ccl.CosmologyVanillaLCDM().to_dict()

    # Create a clean final dict to avoid conflicts between A_s and sigma8
    # that can happen when both are present in defaults
    final_dict = {}

    # Copy all default values first, but be careful about the special case of A_s vs sigma8
    for key, value in cosmo_dict_default.items():
        if key == 'A_s' and 'A_s' in cosmo_dict:
            # If user provided A_s, don't use the default A_s (None)
            # that would conflict with their sigma8 from defaults
            continue
        elif key == 'sigma8' and 'A_s' in cosmo_dict and 'sigma8' not in cosmo_dict:
            # If user specified A_s but didn't specify sigma8, we don't want to use the default sigma8
            # that would conflict with their A_s from defaults
            continue
        else:
            final_dict[key] = value

    # Apply user's overrides (filter out None values to avoid pyccl errors)
    for key, value in cosmo_dict.items():
        if value is not None:
            final_dict[key] = value

    try:
        return ccl.Cosmology(**final_dict)
    except Exception as e:
        # Provide more helpful error message for debugging
        missing_params = [param for param in ['Omega_c', 'Omega_b', 'h'] if param not in final_dict]
        if missing_params:
            raise ValueError(f"Cannot create Cosmology object: Missing required parameters {missing_params}. "
                           f"Provided parameters: {list(final_dict.keys())}") from e
        raise


def load_module_from_path(path):
    """
    Load a module from a given path.

    Parameters
    ----------
    path : str
        Path to the module to load.

    Returns
    -------
    module
        Module loaded from the given path.
    """
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def string_to_seed(seedstring):
    """
    Convert a string to a random seed.

    Parameters
    ----------
    string : str
        String to convert to a random seed.

    Returns
    -------
    int
        Random seed.
    """
    return int(int(hashlib.md5(seedstring.encode('utf-8')).hexdigest(), 16) % 1.e8)


def modify_default_params(default_params, ccl_cosmology, systematics=None):
    """
    Modify the default parameters with the values from the CCL cosmology and
    systematics if provided.

    Parameters
    ----------
    default_params : dict
        Dictionary with the default parameters.
    ccl_cosmology : dict
        Dictionary with the CCL cosmology parameters.
    systematics : dict, optional
        Dictionary with the systematics parameters to override the defaults.

    Returns
    -------
    dict
        Dictionary with the modified default parameters.
    """
    for key, value in default_params.items():
        if key in ccl_cosmology:
            default_params[key] = ccl_cosmology[key]
        elif systematics is not None and key in systematics:
            default_params[key] = systematics[key]
    return default_params
