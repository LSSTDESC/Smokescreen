import pytest  # noqa: F401
import types
import os
import datetime
from unittest.mock import patch, MagicMock  # noqa: F401
import numpy as np
import sacc
import pyccl as ccl
from firecrown.likelihood.likelihood import Likelihood
from firecrown.modeling_tools import ModelingTools
from smokescreen.datavector import ConcealDataVector
ccl.gsl_params.LENSING_KERNEL_SPLINE_INTEGRATION = False

COSMO = ccl.CosmologyVanillaLCDM()


class EmptyLikelihood(Likelihood):
    """
    empty mock likelihood based on:
    https://github.com/LSSTDESC/firecrown/blob/master/tests/likelihood/lkdir/lkmodule.py
    """
    def __init__(self):
        self.nothing = 1.0
        super().__init__()

    def read(self, sacc_data: sacc.Sacc):
        pass

    def compute_loglike(self, ModellingTools):
        return -self.nothing*2.0

    def compute_theory_vector(self, ModellingTools):
        return self.nothing

    def get_data_vector(self):
        return self.nothing


class MockLikelihoodModule(types.ModuleType):
    def build_likelihood(self, *args, **kwargs):
        self.mocktools = ModelingTools()
        self.mocklike = EmptyLikelihood()
        return self.mocklike, self.mocktools

    def compute_theory_vector(self, ModellingTools):
        return self.mocklike.compute_theory_vector(ModellingTools)


class MockCosmo:
    def __init__(self, params):
        self._params = params

    def __getitem__(self, key):
        return self._params[key]


def test_smokescreen_init():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Check that Smokescreen can be instantiated with valid inputs
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)
    assert isinstance(smokescreen, ConcealDataVector)

    # Check that Smokescreen raises an error when given an invalid likelihood
    with pytest.raises(AttributeError):
        invalid_likelihood = types.ModuleType("invalid_likelihood")
        ConcealDataVector(cosmo, invalid_likelihood,
                          shifts_dict, sacc_data, systematics_dict)

    # check if breaks if given a shift with a key not in the cosmology parameters
    with pytest.raises(ValueError):
        invalid_shifts_dict = {"Omega_c": 1, "invalid_key": 1}
        ConcealDataVector(cosmo, likelihood,
                          invalid_shifts_dict, sacc_data, systematics_dict)


def test_load_shifts():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1, "Omega_b": (-1, 2), "sigma8": (2, 3)}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Call load_shifts and get the result
    shifts = smokescreen._load_shifts(seed="2112")

    # Check that the shifts are correct
    assert shifts["Omega_c"] == 1
    assert shifts["Omega_c"] >= 0 and shifts["Omega_b"] <= 3
    assert shifts["sigma8"] >= 2 and shifts["sigma8"] <= 3

    # Check that an error is raised for an invalid tuple
    smokescreen.shifts_dict["Omega_c"] = (1,)
    with pytest.raises(ValueError):
        smokescreen._load_shifts(seed="2112")

    # check if breaks if given a shift with a key not in the cosmology parameters
    smokescreen.shifts_dict["invalid_key"] = 1
    with pytest.raises(ValueError):
        smokescreen._load_shifts(seed="2112")

    # check if break if a a shift type is not flat
    with pytest.raises(NotImplementedError):
        smokescreen._load_shifts(seed="2112", shift_distr="invalid")
    with pytest.raises(NotImplementedError):
        smokescreen = ConcealDataVector(cosmo, likelihood, shifts_dict, sacc_data,
                                        systematics_dict,
                                        **{'shift_distr': 'invalid'})


def test_load_shifts_gaussian():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": (0.3, 0.02), "Omega_b": (0.05, 0.002), "sigma8": (0.82, 0.02)}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'shift_distr': 'gaussian'})

    # Call load_shifts and get the result
    shifts = smokescreen._load_shifts(seed="2112", shift_distr="gaussian")

    # Check that the shifts are correct
    assert shifts["Omega_c"] >= 0.1 and shifts["Omega_c"] <= 0.4
    assert shifts["Omega_b"] >= 0.01 and shifts["Omega_b"] <= 0.05
    assert shifts["sigma8"] >= 0.5 and shifts["sigma8"] <= 1.2


def test_debug_mode(capfd):
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Check that Smokescreen can be instantiated with valid inputs
    _ = ConcealDataVector(cosmo, likelihood,
                          shifts_dict, sacc_data, systematics_dict,
                          **{'debug': True})
    # Capture the output
    out, err = capfd.readouterr()

    # Check that the debug output is correct
    assert "[DEBUG] Shifts: " in out
    assert "[DEBUG] Concealed Cosmology: " in out
    assert f"{shifts_dict}" in out


def test_calculate_concealing_factor_add():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True})

    # Call calculate_concealing_factor with type="add"
    concealing_factor = smokescreen.calculate_concealing_factor(factor_type="add")

    # Check that the concealing (blinding) factor is correct
    assert concealing_factor == smokescreen.theory_vec_conceal - smokescreen.theory_vec_fid


def test_calculate_concealing_factor_add_gaussian():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": (0.3, 0.02), "Omega_b": (0.05, 0.002), "sigma8": (0.82, 0.02)}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True, 'shift_distr': 'gaussian'})

    # Call calculate_concealing_factor with type="add"
    concealing_factor = smokescreen.calculate_concealing_factor(factor_type="add")

    # Check that the concealing (blinding) factor is correct
    assert concealing_factor == smokescreen.theory_vec_conceal - smokescreen.theory_vec_fid


def test_calculate_concealing_factor_mult():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True})

    # Call calculate_concealing_factor with type="add"
    concealing_factor = smokescreen.calculate_concealing_factor(factor_type="mult")

    # Check that the concealing (blinding) factor is correct
    assert concealing_factor == smokescreen.theory_vec_conceal / smokescreen.theory_vec_fid


def test_calculate_concealing_factor_invalid_type():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Call calculate_concealing_factor with an invalid type
    with pytest.raises(NotImplementedError):
        smokescreen.calculate_concealing_factor(factor_type="invalid")


def test_apply_concealing_to_likelihood_datavec_add():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True})

    # Set the concealing (blinding) factor and type
    # Call calculate_concealing_factor with type="add"
    concealing_factor = smokescreen.calculate_concealing_factor(factor_type="add")

    # Call apply_blinding_to_likelihood_datavec
    concealed_data_vector = smokescreen.apply_concealing_to_likelihood_datavec()
    expected_concealed = smokescreen.likelihood.get_data_vector() + concealing_factor

    # Check that the blinded data vector is correct
    assert concealed_data_vector == expected_concealed


def test_apply_concealing_to_likelihood_datavec_mult():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True})

    # Set the concealing (blinding) factor and type
    # Call calculate_concealing_factor with type="add"
    concealing_factor = smokescreen.calculate_concealing_factor(factor_type="mult")

    # Call apply_concealing_to_likelihood_datavec
    concealed_data_vector = smokescreen.apply_concealing_to_likelihood_datavec()
    expected_concealing = smokescreen.likelihood.get_data_vector() * concealing_factor

    # Check that the concealing (blinding) data vector is correct
    assert concealed_data_vector == expected_concealing


def test_apply_concealing_to_likelihood_datavec_invalid_type():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict,
                                    **{'debug': True})

    # Set the expected_concealing factor and type
    # Call calculate_concealing_factor with type="add"
    _ = smokescreen.calculate_concealing_factor(factor_type="mult")
    # Set an invalid type
    smokescreen.factor_type = "invalid"
    with pytest.raises(NotImplementedError):
        smokescreen.apply_concealing_to_likelihood_datavec()


def test_load_likelihood():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc.load_fits("./examples/cosmic_shear/cosmicshear_sacc.fits")
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Test with a valid likelihood module
    likelihood, tools = smokescreen._load_likelihood(likelihood, sacc_data)
    assert isinstance(likelihood, Likelihood)
    assert hasattr(likelihood, 'compute_theory_vector')
    assert hasattr(likelihood, 'get_data_vector')

    # Test with a valid likelihood file path
    likelihood_file_path = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    likelihood, tools = smokescreen._load_likelihood(likelihood_file_path, sacc_data)
    assert isinstance(likelihood, Likelihood)
    assert hasattr(likelihood, 'compute_theory_vector')
    assert hasattr(likelihood, 'get_data_vector')

    # Test with an invalid likelihood (neither a module nor a file path)
    with pytest.raises(TypeError):
        smokescreen._load_likelihood(123, sacc_data)

    # Test with a non-existent likelihood file path
    with pytest.raises(FileNotFoundError):
        smokescreen._load_likelihood("/path/to/nonexistent/file.py", sacc_data)

    # Test with a module that doesn't have a 'build_likelihood' method
    invalid_likelihood = types.ModuleType("invalid_likelihood")
    with pytest.raises(AttributeError):
        smokescreen._load_likelihood(invalid_likelihood, sacc_data)

    # Test with a module that doesn't have a 'build_parameters' input
    invalid_likelihood = types.ModuleType("invalid_likelihood")
    invalid_likelihood.build_likelihood = lambda: None
    with pytest.raises(AssertionError):
        smokescreen._load_likelihood(invalid_likelihood, sacc_data)


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector(mock_getuser):
    # Create mock inputs
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}
    sacc_data = sacc.Sacc.load_fits("./examples/cosmic_shear/cosmicshear_sacc.fits")
    sck = ConcealDataVector(cosmo, likelihood,
                            shift_dict, sacc_data, syst_dict, seed=1234)

    # Calculate the concealing factor and apply it to the likelihood data vector
    sck.calculate_concealing_factor()
    blinded_dv = sck.apply_concealing_to_likelihood_datavec()

    # Save the blinded data vector to a temporary file
    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc"
    temp_file_name = f"{temp_file_path}{temp_file_root}_concealed_data_vector.fits"
    returned_sacc = sck.save_concealed_datavector(temp_file_path,
                                                  temp_file_root,
                                                  return_sacc=True)
    # checks if the return is a sacc object
    assert isinstance(returned_sacc, sacc.Sacc)

    returned_sacc = sck.save_concealed_datavector(temp_file_path,
                                                  temp_file_root,
                                                  return_sacc=False)

    # Check that the return is None
    assert returned_sacc is None

    # Check that the file was created
    assert os.path.exists(temp_file_name)

    # Load the file and check that the data vector matches the blinded data vector
    loaded_sacc = sacc.Sacc.load_fits(temp_file_name)
    np.testing.assert_array_equal(loaded_sacc.mean, blinded_dv)

    info_str = 'Concealed (blinded) data-vector, created by Smokescreen.'
    assert loaded_sacc.metadata['concealed'] is True
    assert loaded_sacc.metadata['creator'] == mock_getuser.return_value
    assert loaded_sacc.metadata['creation'][:10] == datetime.date.today().isoformat()
    assert loaded_sacc.metadata['info'] == info_str
    assert loaded_sacc.metadata['seed_smokescreen'] == 1234
    # Clean up the temporary file
    os.remove(temp_file_name)
