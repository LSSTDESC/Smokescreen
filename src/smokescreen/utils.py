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
    # ensure that if A_s, we set sigma8 to None
    if "A_s" in cosmo_dict.keys():
        cosmo_dict_default["sigma8"] = None
    return ccl.Cosmology(**{**cosmo_dict_default, **cosmo_dict})


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
