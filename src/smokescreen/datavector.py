# author: Arthur Loureiro <arthur.loureiro@fysik.su.se>
# license: BSD 3-Clause
'''
Conceal Data Vector (:mod:`smokescreen.datavector`)
====================================================

.. currentmodule:: smokescreen.datavector

The :mod:`smokescreen.datavector` module provides functionalities
to conceal data vectors in the context of cosmological analysis.


Conceal Data Vector Class
-------------------------

.. autoclass:: ConcealDataVector
   :members:
   :undoc-members:
   :inherited-members:
'''
import os
import types
import inspect
import datetime
import getpass
from copy import deepcopy
import pyccl as ccl
import sacc
from firecrown.likelihood.likelihood import load_likelihood
from firecrown.likelihood.likelihood import load_likelihood_from_module_type
from firecrown.likelihood.likelihood import NamedParameters
from firecrown.parameters import ParamsMap
from firecrown.utils import save_to_sacc

from smokescreen.param_shifts import draw_flat_or_deterministic_param_shifts
from smokescreen.param_shifts import draw_gaussian_param_shifts
from smokescreen.utils import load_module_from_path


class ConcealDataVector():
    """
    Class for calling a smokescreen on the measured data-vector.

    FIXME: Only cosmological parameters are supported for now for the shifts

    Parameters
    ----------
    cosmo : pyccl.Cosmology
        Cosmology object from CCL with a fiducial cosmology.
    systm_dict : dict
        Dictionary of systematics names and corresponding fiducial values.
    likelihood : str or module
        path to the likelihood or a module containing the likelihood
        must contain both `build_likelihood` and `compute_theory_vector` methods
    shifts_dict : dict
        Dictionary of parameter names and corresponding shift widths. If the
        shifts are single values, the dictionary values should be the shift
        widths. If the shifts are tuples of values, the dictionary values
        should be the (lower, upper) bounds of the shift widths.
    sacc_data : sacc.sacc.Sacc
        Data-vector to be concealed (blinded).
        If None, the data-vector will be loaded from the likelihood.
    seed : int or str
        Random seed.

    Keyword Arguments
    -----------------
    shift_type : str
        Type of shift to be applied. Default is "flat".
        ``FIXME: Only flat shifts are implemented for now.``
    debug : bool
        If True, prints debug information. Default is False.


    """
    def __init__(self, cosmo, systm_dict, likelihood, shifts_dict, sacc_data,
                 seed="2112", **kwargs):
        """
        unit
        """
        # save the cosmology
        self.cosmo = cosmo
        # save the systematics dictionary
        self.systematics_dict = systm_dict
        # save the data-vector
        self.sacc_data = sacc_data
        # seed for the random number generator
        self.seed = seed
        # checks if the sacc_data is in the correct format:
        assert isinstance(self.sacc_data, sacc.sacc.Sacc), "sacc_data must be a sacc object"
        # load the likelihood
        self.likelihood, self.tools = self._load_likelihood(likelihood,
                                                            self.sacc_data)

        # save the shifts
        self.shifts_dict = shifts_dict

        # load the systematics
        self.systematics = self._load_systematics(self.systematics_dict, self.likelihood)

        # load the shifts
        # Check for 'shift_type' keyword argument
        if 'shift_distr' in kwargs:
            self.__shifts = self._load_shifts(seed, shift_distr=kwargs['shift_distr'])
        else:
            self.__shifts = self._load_shifts(seed)

        # create concealed cosmology object:
        self.__concealed_cosmo = self._create_concealed_cosmo()

        if 'debug' in kwargs and kwargs['debug']:
            self.__debug = True
            print(f"[DEBUG] Shifts: {self.__shifts}")
            print(f"[DEBUG] Concealed Cosmology: {self.__concealed_cosmo}")
        else:
            self.__debug = False
        # # create the smokescreen data-vector
        # self.smokescreen_data = self.create_smokescreen_data()

    def _load_likelihood(self, likelihood, sacc_data):
        """
        Loads the likelihood either from a python module or from a file.

        Parameters
        ----------
        likelihood : str or module
            path to the likelihood or a module containing the likelihood
            must contain both `build_likelihood` and `compute_theory_vector` methods
        """

        build_parameters = NamedParameters({'sacc_data': sacc_data})

        if type(likelihood) is str:
            # check if the file can be found
            if not os.path.isfile(likelihood):
                raise FileNotFoundError(f'Could not find file {likelihood}')

            # test the likelihood
            self.__test_likelihood(likelihood, 'str')
            # load the likelihood from the file
            likelihood, tools = load_likelihood(likelihood, build_parameters)

            # check if the likelihood has a compute_vector method
            if not hasattr(likelihood, 'compute_theory_vector'):  # pragma: no cover
                raise AttributeError('Likelihood does not have a compute_vector method')
            return likelihood, tools

        elif isinstance(likelihood, types.ModuleType):
            # test the likelihood
            self.__test_likelihood(likelihood, 'module')

            # tries to load the likelihood from the module
            likelihood, tools = load_likelihood_from_module_type(likelihood,
                                                                 build_parameters)
            # check if the likelihood has a compute_vector method
            if not hasattr(likelihood, 'compute_theory_vector'):  # pragma: no cover
                raise AttributeError('Likelihood does not have a compute_vector method')
            return likelihood, tools
        else:
            raise TypeError('Likelihood must be a string path to a likelihood module or a module')

    def __test_likelihood(self, likelihood, like_type):
        """
        Tests if the likelihood has the required methods.

        Parameters
        ----------
        likelihood : str or module
            path to the likelihood or a module containing the likelihood
            must contain both `build_likelihood` and `compute_theory_vector` methods
        like_type : str
            Type of likelihood. Can be either 'str' or 'module'.
        """
        if like_type == "str":
            likelihood = load_module_from_path(likelihood)
        else:
            likelihood = likelihood

        # check if the module has a build_likelihood method
        if not hasattr(likelihood, 'build_likelihood'):
            raise AttributeError('Likelihood does not have a build_likelihood method')

        if self.sacc_data is not None:
            sig = inspect.signature(likelihood.build_likelihood)
            likefunc_params = sig.parameters
            assert len(likefunc_params) >= 1, ("A sacc was provided, ",
                                               "the likelihood must require a",
                                               "build_parameters NamedParameters object!")

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

    def _load_shifts(self, seed, shift_distr="flat"):
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
        if shift_distr == "flat":
            return draw_flat_or_deterministic_param_shifts(self.cosmo, self.shifts_dict, seed)
        elif shift_distr == "gaussian":
            return draw_gaussian_param_shifts(self.cosmo, self.shifts_dict, seed)
        else:
            raise NotImplementedError('Only flat and gaussian shifts are implemented')

    def _create_concealed_cosmo(self):
        """
        Creates a blinded cosmology object with the shifts applied.

        FIXME: Unsure this is the best way of doing this but it is similar to what is done in Augur.
        """
        concealed_cosmo_dict = deepcopy(self.cosmo.to_dict())
        # sometimes we have this extra paramters that can cause problems:
        try:
            del concealed_cosmo_dict['extra_parameters']
        except KeyError:  # pragma: no cover
            pass
        for k in self.__shifts.keys():
            concealed_cosmo_dict[k] = self.__shifts[k]
        concealed_cosmo = ccl.Cosmology(**concealed_cosmo_dict)
        return concealed_cosmo

    def calculate_concealing_factor(self, factor_type="add"):
        r"""
        Calculates the concealing (blinding) factor for the data-vector,
            according to Muir et al. 2019:

        Parameters
        ----------
        factor_type : str
            Type of concealing (blinding) factor to be calculated. Default is ``add``.

        Returns
        -------
        .__concealing_factor : np.ndarray
            Concealing factor.

        Notes
        -----
        type="add":
            .. math::
                f^{\rm add} = d(\theta_{\rm blind}) - d(\theta_{\rm fid})

        type="mult":
            .. math::
                f^{\rm mult} = d(\theta_{\rm blind}) / d(\theta_{\rm fid})
        """
        self.factor_type = factor_type
        # update the tools:
        self.tools.update({})
        # prepare the original cosmology tools:
        self.tools.prepare(self.cosmo)
        # update the likelihood with the systematics parameters:
        self.likelihood.update(self.systematics)
        # fiducial theory vector:
        self.theory_vec_fid = self.likelihood.compute_theory_vector(self.tools)
        # resets the likelihood and tools
        self.likelihood.reset()
        self.tools.reset()

        # now calculates the shifted theory vector:
        # update the tools:
        self.tools.update({})
        # prepare the original cosmology tools:
        self.tools.prepare(self.__concealed_cosmo)
        # update the likelihood with the systematics parameters:
        self.likelihood.update(self.systematics)
        # concealed theory vector:
        self.theory_vec_conceal = self.likelihood.compute_theory_vector(self.tools)

        if self.factor_type == "add":
            self.__concealing_factor = self.theory_vec_conceal - self.theory_vec_fid
        elif self.factor_type == "mult":
            self.__concealing_factor = self.theory_vec_conceal / self.theory_vec_fid
        else:
            raise NotImplementedError('Only "add" and "mult" concealing factor is implemented')
        if self.__debug:
            return self.__concealing_factor

    def apply_concealing_to_likelihood_datavec(self):
        """
        Applies the concealing (blinding) factor to the data-vector.
        """
        self.data_vector = self.likelihood.get_data_vector()
        if self.factor_type == "add":
            self.concealed_data_vector = self.data_vector + self.__concealing_factor
        elif self.factor_type == "mult":
            self.concealed_data_vector = self.data_vector * self.__concealing_factor
        else:
            raise NotImplementedError('Only "add" and "mult" blinding factor is implemented')
        return self.concealed_data_vector

    def save_concealed_datavector(self, path_to_save, file_root,
                                  return_sacc=False):
        """
        Saves the concealed (blinded) data-vector to a file.

        Saves the blinded data-vector to a file with the name:
        ``{path_to_save}/{file_root}_blinded_data_vector.fits``

        Parameters
        ----------
        path_to_save : str
            Path to save the blinded data-vector.
        file_root : str
            Root of the file name.
        return_sacc : bool
            If True, returns the sacc object with the blinded data-vector.


        """
        idx = self.likelihood.get_sacc_indices()
        concealed_sacc = save_to_sacc(self.sacc_data,
                                      self.concealed_data_vector,
                                      idx)
        # copies the metadata from the original sacc file:
        concealed_sacc.metadata = self.sacc_data.metadata
        # adds metadata to the sacc file:
        concealed_sacc.metadata['concealed'] = True
        concealed_sacc.metadata['creator'] = getpass.getuser()
        concealed_sacc.metadata['creation'] = datetime.datetime.now().isoformat()
        concealed_sacc.metadata['info'] = 'Concealed (blinded) data-vector, created by Smokescreen.'
        concealed_sacc.metadata['seed_smokescreen'] = self.seed
        concealed_sacc.save_fits(f"{path_to_save}/{file_root}_concealed_data_vector.fits",
                                 overwrite=True)
        if return_sacc:
            return concealed_sacc
        else:
            return None

    # def encrypt_original_datavector(self, original_sacc_file, path_to_save, keep_original=False):
    #     """
    #     Encrypts the original data-vector.

    #     Parameters
    #     ----------
    #     keep_original : bool
    #         If True, keeps the original data-vector file. Default is False.
    #     """

    #     encrypt_file(original_sacc_file, path_to_save, save_file=True,
    #                  keep_original=keep_original)

    #     if self.__debug:
    #         print(f"[DEBUG] Original data-vector encrypted successfully.")
    #         encry_file_name = f"{path_to_save}/{os.path.basename
    # (original_sacc_file).split('.')[0]}"
    #         print(f"[DEBUG] Key saved as {encry_file_name}.key")
