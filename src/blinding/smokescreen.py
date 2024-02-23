import numpy as np
import os 
import types
from copy import deepcopy
import pyccl as ccl
from firecrown.likelihood.likelihood import load_likelihood
from firecrown.likelihood.likelihood import load_likelihood_from_module_type
from firecrown.parameters import ParamsMap

from blinding.param_shifts import draw_flat_or_deterministic_param_shifts


# creates the smokescreen object
class Smokescreen():
    """
    Class for calling a smokescreen on the measured data-vector.
    """
    def __init__(self, cosmo, systm_dict, sacc_data, likelihood, shifts_dict, seed="2112", **kwargs):
        """
        Parameters
        ----------
        cosmo : pyccl.Cosmology
            Cosmology object from CCL with a fiducial cosmology.
        systm_dict : dict
            Dictionary of systematics names and corresponding fiducial values.
        sacc_data : sacc.sacc.Sacc
            Data-vector to be blinded.
        likelihood : str or module
            path to the likelihood or a module containing the likelihood
            must contain both `build_likelihood` and `compute_theory_vector` methods
        shifts_dict : dict
            Dictionary of parameter names and corresponding shift widths. If the
            shifts are single values, the dictionary values should be the shift
            widths. If the shifts are tuples of values, the dictionary values
            should be the (lower, upper) bounds of the shift widths.
        seed : int or str
            Random seed.

        kwargs
        ------
        shift_type : str
            Type of shift to be applied. Default is "flat".
            FIXME: Only flat shifts are implemented for now.
        debug : bool
            If True, prints debug information. Default is False.

        # FIXME: Only cosmological parameters are supported for now for the shifts
        """
        # save the cosmology
        self.cosmo = cosmo
        # save the systematics dictionary
        self.systematics_dict = systm_dict
        # save the data-vector
        self.sacc_data = sacc_data
        # load the likelihood
        self.likelihood, self.tools = self._load_likelihood(likelihood)
        # save the shifts
        self.shifts_dict = shifts_dict

        # makes a deep copy of the tools for the blinded cosmology:
        self._tools_blinding = deepcopy(self.tools)

        # load the systematics
        self.systematics = self._load_systematics(self.systematics_dict, self.likelihood)

        # load the shifts
        # Check for 'shift_type' keyword argument
        if 'shift_type' in kwargs:
            self.__shifts = self._load_shifts(seed, shift_type=kwargs['shift_type'])
        else:
            self.__shifts = self._load_shifts(seed)

        # create blinded cosmology object:
        self.__blinded_cosmo = self._create_blinded_cosmo()

        if 'debug' in kwargs and kwargs['debug']:
            self.__debug = True
            print(f"[DEBUG] Shifts: {self.__shifts}")
            print(f"[DEBUG] Blinded Cosmology: {self.__blinded_cosmo}")
        else:
            self.__debug = False
        # # create the smokescreen data-vector
        # self.smokescreen_data = self.create_smokescreen_data()

    def _load_likelihood(self, likelihood):
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

    def _load_systematics(self, systematics_dict, likelihood):
        """
        Loads the systematics from the systematics dictionary.

        Parameters
        ----------
        systematics_dict : dict
            Dictionary of systematics names and corresponding fiducial values.
        """
        likelihood_req_systematics = list(likelihood.required_parameters().get_params_names())
        # test if all keys in the systematics_dict are in the likelihood systematics:
        for key in likelihood_req_systematics:
            if key not in systematics_dict.keys():
                raise ValueError(f"Systematic {key} not in likelihood systematics")
        return ParamsMap(systematics_dict)

    def _load_shifts(self, seed, shift_type="flat"):
        """
        Loads the shifts from the shifts dictionary.

        Parameters
        ----------
        shifts_dict : dict
            Dictionary of parameter names and corresponding shift widths. If the
            shifts are single values, it does a deterministic shift: PARAM = FIDUCIAL + SHIFT
            If the shifts are tuples of values, the dictionary values
            should be the (lower, upper) bounds of the shift widths: PARAM = U(a, b)
            If the first valuee is negative, it is assumed that the parameter
            is to be shifted from the fiducial value: PARAM = FIDUCIAL + U(-a, b)
        """
        if shift_type == "flat":
            return draw_flat_or_deterministic_param_shifts(self.cosmo, self.shifts_dict, seed)
        else:
            raise NotImplementedError('Only flat shifts are implemented')

    def _create_blinded_cosmo(self):
        """
        Creates a blinded cosmology object with the shifts applied.

        FIXME: Unsure this is the best way of doing this but it is similar to what is done in Augur.
        """
        blinded_cosmo_dict = deepcopy(self.cosmo._params_init_kwargs)
        # sometimes we have this extra paramters that can cause problems:
        try:
            del blinded_cosmo_dict['extra_parameters']
        except KeyError:
            pass
        for k in self.__shifts.keys():
            blinded_cosmo_dict[k] = self.__shifts[k]
        blinded_cosmo = ccl.Cosmology(**blinded_cosmo_dict)
        return blinded_cosmo

    def calculate_blinding_factor(self, type="add"):
        """
        Calculates the blinding factor for the data-vector, according to Muir et al. 2019:

        type='add':
            $f^add = d(\theta_blind) - d(\theta_fid)$

        type='mult':
            $f^mult = d(\theta_blind) / d(\theta_fid)$
        Parameters
        ----------
        type : str
            Type of blinding factor to be calculated. Default is "add".
        """
        self.type = type
        # update the tools:
        self.tools.update({})
        self._tools_blinding.update({})

        # prepare the original cosmology tools:
        self.tools.prepare(self.cosmo)
        # prepare the blinded cosmology tools:
        self._tools_blinding.prepare(self.__blinded_cosmo)

        # update the likelihood with the systematics parameters:
        self.likelihood.update(self.systematics)

        # fiducial theory vector:
        self.theory_vec_fid = self.likelihood.compute_theory_vector(self.tools)
        # blinded theory vector:
        self.theory_vec_blind = self.likelihood.compute_theory_vector(self._tools_blinding)
        #return theory_vector

        if self.type == "add":
            self.__blinding_factor = self.theory_vec_blind - self.theory_vec_fid
        elif self.type == "mult":
            self.__blinding_factor = self.theory_vec_blind / self.theory_vec_fid
        else:
            raise NotImplementedError('Only "add" and "mult" blinding factor is implemented')
        if self.__debug:
            return self.__blinding_factor

    def apply_blinding_to_likelihood_datavec(self):
        """
        Applies the blinding factor to the data-vector.
        """
        self.data_vector = self.likelihood.get_data_vector()
        if self.type == "add":
            self.blinded_data_vector = self.data_vector + self.__blinding_factor
        elif self.type == "mult":
            self.blinded_data_vector = self.data_vector * self.__blinding_factor
        else:
            raise NotImplementedError('Only "add" and "mult" blinding factor is implemented')
        return self.blinded_data_vector