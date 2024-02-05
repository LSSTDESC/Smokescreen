import pytest
import types
import sacc
from firecrown.likelihood.likelihood import Likelihood
from firecrown.modeling_tools import ModelingTools
from blinding.smokescreen import Smokescreen

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
    def compute_theory_vector(self):
        return self.nothing

class MockLikelihoodModule(types.ModuleType):
    def build_likelihood(self, *args, **kwargs):
        mocktools = ModelingTools()
        mocklike = EmptyLikelihood()
        return mocklike, mocktools

    def compute_theory_vector(self):
        return None

class MockCosmo:
    def __init__(self, params):
        self._params = params

    def __getitem__(self, key):
        return self._params[key]

def test_smokescreen_init():
    # Create mock inputs
    cosmo = "cosmo"
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"param1": 1}

    # Check that Smokescreen can be instantiated with valid inputs
    smokescreen = Smokescreen(cosmo, sacc_data, likelihood, systematics_dict, shifts_dict)
    assert isinstance(smokescreen, Smokescreen)

    # Check that Smokescreen raises an error when given an invalid likelihood
    with pytest.raises(AttributeError):
        invalid_likelihood = types.ModuleType("invalid_likelihood")
        Smokescreen(cosmo, sacc_data, invalid_likelihood, systematics_dict, shifts_dict)

def test_load_shifts():
    # Create mock inputs
    cosmo = MockCosmo({"param1": 1, "param2": 2, "param3": 3})
    sacc_data = "sacc_data"
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"param1": 1, "param2": (-1, 2), "param3": (2, 3), "param4": 4}

    # Instantiate Smokescreen
    smokescreen = Smokescreen(cosmo, sacc_data, likelihood, systematics_dict, shifts_dict)

    # Call load_shifts and get the result
    shifts = smokescreen.load_shifts(seed="2112")

    # Check that the shifts are correct
    assert shifts["param1"] == 1
    assert shifts["param2"] >= 0 and shifts["param2"] <= 3
    assert shifts["param3"] >= 2 and shifts["param3"] <= 3
    assert "param4" not in shifts

    # Check that an error is raised for an invalid tuple
    smokescreen.shifts_dict["param1"] = (1,)
    with pytest.raises(ValueError):
        smokescreen.load_shifts(seed="2112")