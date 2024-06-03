import hashlib
import numpy as np
import importlib.util
import pyccl as ccl

def load_cosmology_from_partial_dict(cosmo_dict):
    """
    Given a partial dictionary with cosmological parameters, return a Cosmology 
    object setting the unspecified parameters to their default values.
    """
    # sets the default values for the cosmological parameters
    cosmo_dict_default = ccl.CosmologyVanillaLCDM()._params_init_kwargs
    # test that keys in cosmo_dict are in cosmo_dict_default
    for key in cosmo_dict:
        if key not in cosmo_dict_default.keys():
            raise ValueError(f"Invalid cosmology parameter: {key}")
    for key in cosmo_dict_default:
        if key in cosmo_dict:
            # we cannot pass both A_s and sigma8!
            if key == 'A_s':
                cosmo_dict_default['sigma8'] = None
            elif key == 'sigma8':
                cosmo_dict_default['A_s'] = None
            cosmo_dict_default[key] = cosmo_dict[key]
    try:
        return ccl.Cosmology(**cosmo_dict_default)
    except ValueError:
        raise ValueError("Invalid cosmology parameters.")

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