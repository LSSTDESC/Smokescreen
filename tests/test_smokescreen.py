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