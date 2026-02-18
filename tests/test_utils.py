import pytest  # noqa  F401
import tempfile
import os
import numpy as np
import pyccl as ccl
from smokescreen.utils import string_to_seed, load_module_from_path
from smokescreen.utils import load_cosmology_from_partial_dict


def test_load_module_from_path():
    # Create a temporary Python module
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
        temp.write(b"def test_function():\n    return 'Hello, World!'")
        temp_path = temp.name

    # Load the module using the function
    module = load_module_from_path(temp_path)

    # Check that the function from the module can be called
    assert module.test_function() == 'Hello, World!'

    # Clean up the temporary file
    os.remove(temp_path)


def test_string_to_seed():
    seed_string = "test_seed"
    result = string_to_seed(seed_string)

    # Check that the result is an integer
    assert isinstance(result, int)

    # Check that the same string produces the same seed
    assert string_to_seed(seed_string) == result

    # Check that a different string produces a different seed
    assert string_to_seed("different_seed") != result


def test_load_cosmology_from_partial_dict():
    # Test with valid cosmological parameters
    cosmo_dict = {"Omega_c": 0.27, "sigma8": 0.8}
    cosmo = load_cosmology_from_partial_dict(cosmo_dict)
    assert isinstance(cosmo, ccl.Cosmology)
    assert cosmo["Omega_c"] == 0.27
    assert cosmo["sigma8"] == 0.8

    # Test with A_s in the dictionary
    cosmo_dict = {"A_s": 2.1e-9}
    cosmo = load_cosmology_from_partial_dict(cosmo_dict)
    assert cosmo["A_s"] == 2.1e-9
    assert np.isnan(cosmo["sigma8"])


def test_load_cosmology_from_partial_dict_conflicting_params():
    # Test with both A_s and sigma8 provided (conflicting parameters)
    # This should raise a ValueError from pyccl about conflicting parameters
    cosmo_dict = {"A_s": 2.1e-9, "sigma8": 0.8}
    with pytest.raises(ValueError) as exc_info:
        load_cosmology_from_partial_dict(cosmo_dict)

    # The error message should indicate the conflicting parameters issue
    assert "a_s" in str(exc_info.value).lower() and "sigma8" in str(exc_info.value).lower()


def test_load_cosmology_from_partial_dict_invalid_type():
    # Test with an invalid parameter type (string instead of number)
    # This should raise a TypeError from pyccl
    cosmo_dict = {"Omega_c": "invalid", "sigma8": 0.8}
    with pytest.raises(TypeError):
        load_cosmology_from_partial_dict(cosmo_dict)
