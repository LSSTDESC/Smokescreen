import pytest  # noqa  F401
import tempfile
import os
import numpy as np
import pyccl as ccl
from smokescreen.utils import string_to_seed, load_module_from_path
from smokescreen.utils import load_cosmology_from_partial_dict
from smokescreen.utils import load_sacc_file


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


class TestLoadSaccFile:
    """Tests for the load_sacc_file utility function."""

    def test_load_sacc_file_fits_format(self, tmp_path):
        import sacc as sacc_mod
        # Create a FITS SACC file
        sacc_data = sacc_mod.Sacc()
        sacc_data.add_tracer('misc', 'test')
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
        fits_path = tmp_path / "test.fits"
        sacc_data.save_fits(str(fits_path))

        # Load using load_sacc_file
        loaded_sacc, file_format = load_sacc_file(str(fits_path))

        assert isinstance(loaded_sacc, sacc_mod.Sacc)
        assert file_format == 'fits'
        assert len(loaded_sacc.mean) == 1

    def test_load_sacc_file_hdf5_format(self, tmp_path):
        import sacc as sacc_mod
        # Create an HDF5 SACC file
        sacc_data = sacc_mod.Sacc()
        sacc_data.add_tracer('misc', 'test')
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
        hdf5_path = tmp_path / "test.hdf5"
        sacc_data.save_hdf5(str(hdf5_path))

        # Load using load_sacc_file
        loaded_sacc, file_format = load_sacc_file(str(hdf5_path))

        assert isinstance(loaded_sacc, sacc_mod.Sacc)
        assert file_format == 'hdf5'
        assert len(loaded_sacc.mean) == 1

    def test_load_sacc_file_with_h5_extension(self, tmp_path):
        import sacc as sacc_mod
        # Create an HDF5 SACC file with .hdf5 extension
        sacc_data = sacc_mod.Sacc()
        sacc_data.add_tracer('misc', 'test')
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
        h5_path = tmp_path / "test.hdf5"
        sacc_data.save_hdf5(str(h5_path))

        # Load using load_sacc_file - should detect as HDF5 regardless of extension
        loaded_sacc, file_format = load_sacc_file(str(h5_path))

        assert isinstance(loaded_sacc, sacc_mod.Sacc)
        assert file_format == 'hdf5'

    def test_load_sacc_file_with_sacc_extension_hdf5(self, tmp_path):
        import sacc as sacc_mod
        # Create an HDF5 SACC file with .sacc extension (like sn_datavector.sacc)
        sacc_data = sacc_mod.Sacc()
        sacc_data.add_tracer('misc', 'test')
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
        sacc_path = tmp_path / "test.sacc"
        sacc_data.save_hdf5(str(sacc_path))

        # Load using load_sacc_file - should detect as HDF5 even with .sacc extension
        loaded_sacc, file_format = load_sacc_file(str(sacc_path))

        assert isinstance(loaded_sacc, sacc_mod.Sacc)
        assert file_format == 'hdf5'

    def test_load_sacc_file_nonexistent(self):
        # Test loading a nonexistent file
        with pytest.raises(ValueError) as exc_info:
            load_sacc_file("nonexistent_file.sacc")
        assert "Cannot load SACC file" in str(exc_info.value)

    def test_load_sacc_file_invalid_fits(self, tmp_path):
        # Create an invalid FITS file (not a SACC file)
        invalid_path = tmp_path / "invalid.fits"
        with open(invalid_path, "w") as f:
            f.write("This is not a valid FITS file")

        # Test that it raises ValueError
        with pytest.raises(ValueError):
            load_sacc_file(str(invalid_path))
