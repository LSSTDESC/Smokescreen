import numpy as np
import os 
import types
import pyccl as ccl
from firecrown.likelihood.likelihood import load_likelihood
from firecrown.likelihood.likelihood import load_likelihood_from_module_type
from firecrown.parameters import ParamsMap


# creates the smokescreen object
class Smokescreen():
    """
    Class for calling a smokescreen on the measured data-vector.
    """
    def __init__(self, cosmo, sacc_data, likelihood, systematics_dict, shifts_dict, **kwargs):
        """
        Parameters
        ----------
        cosmo : pyccl.Cosmology
            Cosmology object from CCL with a fiducial cosmology.
        sacc_data : sacc.sacc.Sacc
            Data-vector to be blinded.
        likelihood : str or module
            path to the likelihood or a module containing the likelihood
            must contain both `build_likelihood` and `compute_theory_vector` methods
        systematics_dict : dict
            Dictionary of systematics names and corresponding fiducial values.
        shifts_dict : dict
            Dictionary of parameter names and corresponding shift widths. If the
            shifts are single values, the dictionary values should be the shift
            widths. If the shifts are tuples of values, the dictionary values
            should be the (lower, upper) bounds of the shift widths.
        """
        # save the cosmology
        self.cosmo = cosmo
        # save the data-vector
        self.sacc_data = sacc_data
        # load the likelihood
        self.likelihood, self.tools = self.load_likelihood(likelihood, **kwargs)

        # # load the systematics
        # self.systematics = self.load_systematics(systematics_dict)
        # # load the shifts
        # self.shifts = self.load_shifts(shifts_dict)
        # # create the smokescreen data-vector
        # self.smokescreen_data = self.create_smokescreen_data()

    def load_likelihood(self, likelihood):
        """
        Loads the likelihood either from a python module or from a file.

        Parameters
        ----------
        likelihood : str or module
            path to the likelihood or a module containing the likelihood
            must contain both `build_likelihood` and `compute_theory_vector` methods
        """
        if type(likelihood) == str:
            # check if the file can be found
            if not os.path.isfile(likelihood):
                raise FileNotFoundError(f'Could not find file {likelihood}')
            # load the likelihood from the file
            likelihood, tools = load_likelihood(likelihood, None)
            # check if the likehood has a compute_vector method
            if not hasattr(likelihood, 'compute_theory_vector'):
                raise AttributeError('Likelihood does not have a compute_vector method')
            return likelihood, tools
        elif isinstance(likelihood, types.ModuleType):
            # check if the module has a build_likelihood method
            if not hasattr(likelihood, 'build_likelihood'):
                raise AttributeError('Likelihood does not have a build_likelihood method')
            # tries to load the likelihood from the module
            likelihood, tools = load_likelihood_from_module_type(likelihood, None)
            # check if the likehood has a compute_vector method
            if not hasattr(likelihood, 'compute_theory_vector'):
                raise AttributeError('Likelihood does not have a compute_vector method')
            return likelihood, tools 
