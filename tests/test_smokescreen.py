import pytest
import types
import sacc
import pyccl as ccl
from firecrown.likelihood.likelihood import Likelihood
from firecrown.modeling_tools import ModelingTools
from blinding.smokescreen import Smokescreen

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
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Check that Smokescreen can be instantiated with valid inputs
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, shifts_dict)
    assert isinstance(smokescreen, Smokescreen)

    # Check that Smokescreen raises an error when given an invalid likelihood
    with pytest.raises(AttributeError):
        invalid_likelihood = types.ModuleType("invalid_likelihood")
        Smokescreen(cosmo, systematics_dict, sacc_data, invalid_likelihood, shifts_dict)

    # check if breaks if given a shift with a key not in the cosmology parameters
    with pytest.raises(ValueError):
        invalid_shifts_dict = {"Omega_c": 1, "invalid_key": 1}
        Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, invalid_shifts_dict)

def test_load_shifts():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1, "Omega_b": (-1, 2), "sigma8": (2, 3)}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, shifts_dict)

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
        smokescreen._load_shifts(seed="2112", shift_type="invalid")
    with pytest.raises(NotImplementedError):
        smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, shifts_dict, **{'shift_type': 'invalid'})

def test_debug_mode(capfd):
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Check that Smokescreen can be instantiated with valid inputs
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, 
                              shifts_dict, **{'debug': True})
     # Capture the output
    out, err = capfd.readouterr()

    # Check that the debug output is correct
    assert "[DEBUG] Shifts: " in out
    assert "[DEBUG] Blinded Cosmology: " in out
    assert f"{shifts_dict}" in out

def test_calculate_blinding_factor_add():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, 
                              shifts_dict, **{'debug': True})

    # Call calculate_blinding_factor with type="add"
    blinding_factor = smokescreen.calculate_blinding_factor(type="add")

    # Check that the blinding factor is correct
    assert blinding_factor == smokescreen.theory_vec_blind - smokescreen.theory_vec_fid

def test_calculate_blinding_factor_mult():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, 
                              shifts_dict, **{'debug': True})

    # Call calculate_blinding_factor with type="add"
    blinding_factor = smokescreen.calculate_blinding_factor(type="mult")

    # Check that the blinding factor is correct
    assert blinding_factor == smokescreen.theory_vec_blind / smokescreen.theory_vec_fid

def test_calculate_blinding_factor_invalid_type():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood, shifts_dict)

    # Call calculate_blinding_factor with an invalid type
    with pytest.raises(NotImplementedError):
        smokescreen.calculate_blinding_factor(type="invalid")

def test_apply_blinding_to_likelihood_datavec_add():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood,
                              shifts_dict, **{'debug': True})

    # Set the blinding factor and type
    # Call calculate_blinding_factor with type="add"
    blinding_factor = smokescreen.calculate_blinding_factor(type="add")

    # Call apply_blinding_to_likelihood_datavec
    blinded_data_vector = smokescreen.apply_blinding_to_likelihood_datavec()
    expected_blinded = smokescreen.likelihood.get_data_vector() + blinding_factor

    # Check that the blinded data vector is correct
    assert blinded_data_vector == expected_blinded

def test_apply_blinding_to_likelihood_datavec_mult():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, systematics_dict, sacc_data, likelihood,
                              shifts_dict, **{'debug': True})

    # Set the blinding factor and type
    # Call calculate_blinding_factor with type="add"
    blinding_factor = smokescreen.calculate_blinding_factor(type="mult")

    # Call apply_blinding_to_likelihood_datavec
    blinded_data_vector = smokescreen.apply_blinding_to_likelihood_datavec()
    expected_blinded = smokescreen.likelihood.get_data_vector() * blinding_factor

    # Check that the blinded data vector is correct
    assert blinded_data_vector == expected_blinded