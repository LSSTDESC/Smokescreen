import types
import sacc
import pyccl as ccl
from firecrown.likelihood.likelihood import Likelihood
from firecrown.modeling_tools import ModelingTools
from ..test_smokescreen import EmptyLikelihood
ccl.gsl_params.LENSING_KERNEL_SPLINE_INTEGRATION = False

COSMO = ccl.CosmologyVanillaLCDM()

class MockLikelihoodModule(types.ModuleType):
    def build_likelihood(self, *args, **kwargs):
        self.mocktools = ModelingTools()
        self.mocklike = EmptyLikelihood()
        return self.mocklike, self.mocktools

    def compute_theory_vector(self, ModellingTools):
        return self.mocklike.compute_theory_vector(ModellingTools)
