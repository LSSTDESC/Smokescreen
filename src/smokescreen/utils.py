import hashlib
import importlib.util
import pyccl as ccl


def load_cosmology_from_partial_dict(cosmo_dict):
    """
    Given a partial dictionary with cosmological parameters, return a Cosmology
    object setting the unspecified parameters to their default values.
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
