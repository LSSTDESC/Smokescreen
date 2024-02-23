import hashlib
import numpy as np
import importlib.util

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