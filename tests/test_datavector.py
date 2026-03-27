import pytest  # noqa: F401
import types
import os
import datetime
from unittest.mock import patch, MagicMock  # noqa: F401
from packaging.version import Version
import numpy as np
import sacc
import pyccl as ccl
import firecrown
import shutil

# Handle different Firecrown versions
if Version(firecrown.__version__) >= Version("1.15.0a0"):
    from firecrown.likelihood import Likelihood
else:
    from firecrown.likelihood.likelihood import Likelihood

from firecrown.modeling_tools import ModelingTools
from smokescreen.datavector import ConcealDataVector
from smokescreen.utils import load_sacc_file

ccl.gsl_params.LENSING_KERNEL_SPLINE_INTEGRATION = False

COSMO = ccl.CosmologyVanillaLCDM()


@pytest.fixture
def fits_sacc_file(tmp_path):
    """Create a FITS-format SACC file for testing."""
    sacc_data = sacc.Sacc()
    # Add tracers matching cosmic shear example (src0, src1)
    sacc_data.add_tracer('sp', 'src0')
    sacc_data.add_tracer('sp', 'src1')
    # Add data points with realistic values
    n_ell = 5
    ell = np.logspace(np.log10(10), np.log10(1000), n_ell)
    for e in ell:
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src0', 'src0'), 1e-7, ell=e)
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src0', 'src1'), 5e-8, ell=e)
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src1', 'src1'), 2e-7, ell=e)

    # Set mean (3 tracers * 5 ell values = 15 data points)
    n_data = len(ell) * 3
    sacc_data.mean = np.ones(n_data) * 1e-7
    sacc_data.add_covariance(np.eye(n_data) * 1e-14)

    # Save to FITS file
    fits_file = tmp_path / "test_sacc.fits"
    sacc_data.save_fits(str(fits_file))

    return str(fits_file), sacc_data


@pytest.fixture
def hdf5_sacc_file(tmp_path):
    """Create an HDF5-format SACC file for testing."""
    sacc_data = sacc.Sacc()
    # Add tracers matching cosmic shear example (src0, src1)
    sacc_data.add_tracer('sp', 'src0')
    sacc_data.add_tracer('sp', 'src1')
    # Add data points with realistic values
    n_ell = 5
    ell = np.logspace(np.log10(10), np.log10(1000), n_ell)
    for e in ell:
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src0', 'src0'), 1e-7, ell=e)
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src0', 'src1'), 5e-8, ell=e)
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('src1', 'src1'), 2e-7, ell=e)

    # Set mean (3 tracers * 5 ell values = 15 data points)
    n_data = len(ell) * 3
    sacc_data.mean = np.ones(n_data) * 1e-7
    sacc_data.add_covariance(np.eye(n_data) * 1e-14)

    # Save to HDF5 file
    hdf5_file = tmp_path / "test_sacc.hdf5"
    sacc_data.save_hdf5(str(hdf5_file))

    return str(hdf5_file), sacc_data


@pytest.fixture
def cosmic_shear_resources(tmp_path):
    """Copy cosmic shear example files to a temp directory for testing."""
    # Copy the likelihood file and SACC files
    source_dir = os.path.join(os.path.dirname(__file__), '..', 'examples', 'cosmic_shear')

    # Copy likelihood file
    likelihood_src = os.path.join(source_dir, 'cosmicshear_likelihood.py')
    likelihood_dst = str(tmp_path / 'cosmicshear_likelihood.py')
    shutil.copy2(likelihood_src, likelihood_dst)

    # Copy FITS SACC file
    fits_src = os.path.join(source_dir, 'cosmicshear_sacc.fits')
    fits_dst = str(tmp_path / 'cosmicshear_sacc.fits')
    shutil.copy2(fits_src, fits_dst)

    # Copy HDF5 SACC file
    hdf5_src = os.path.join(source_dir, 'cosmicshear_sacc.hdf5')
    hdf5_dst = str(tmp_path / 'cosmicshear_sacc.hdf5')
    shutil.copy2(hdf5_src, hdf5_dst)

    return {
        'likelihood': likelihood_dst,
        'fits_sacc': fits_dst,
        'hdf5_sacc': hdf5_dst
    }


class EmptyLikelihood(Likelihood):
    """
    empty mock likelihood based on:
    https://github.com/LSSTDESC/firecrown/blob/master/tests/likelihood/lkdir/lkmodule.py
    """
    def __init__(self):
        self.nothing = 1.0
        self._data_vector = np.array([1.0, 2.0, 3.0])
        self._covariance = np.eye(3) * 0.1
        super().__init__()

    def read(self, sacc_data: sacc.Sacc):
        pass

    def compute_loglike(self, ModellingTools):
        return -self.nothing*2.0

    def compute_theory_vector(self, ModellingTools):
        return self.nothing

    def get_data_vector(self):
        return self._data_vector

    def get_cov(self):
        return self._covariance


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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(n_data) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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


def test_verify_sacc_consistency_matching():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Create a mock likelihood with matching data
    mock_likelihood = MagicMock()
    mock_likelihood.get_data_vector.return_value = np.array([1.0, 2.0, 3.0])
    mock_likelihood.get_cov.return_value = np.eye(3) * 0.1

    # Test that no error is raised for matching data
    smokescreen._verify_sacc_consistency(mock_likelihood)


def test_verify_sacc_consistency_mismatch_data_vector():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Create a mock likelihood with mismatched data vector
    mock_likelihood = MagicMock()
    mock_likelihood.get_data_vector.return_value = np.array([2.0, 3.0, 4.0])  # Different values
    mock_likelihood.get_cov.return_value = np.eye(3) * 0.1

    # Test that ValueError is raised for mismatched data vector
    with pytest.raises(ValueError) as exc_info:
        smokescreen._verify_sacc_consistency(mock_likelihood)

    assert "Data vector mismatch" in str(exc_info.value)


def test_verify_sacc_consistency_mismatch_covariance():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Create a mock likelihood with mismatched covariance
    mock_likelihood = MagicMock()
    mock_likelihood.get_data_vector.return_value = np.array([1.0, 2.0, 3.0])
    mock_likelihood.get_cov.return_value = np.eye(3) * 0.5  # Different variance

    # Test that ValueError is raised for mismatched covariance
    with pytest.raises(ValueError) as exc_info:
        smokescreen._verify_sacc_consistency(mock_likelihood)

    assert "Covariance matrix mismatch" in str(exc_info.value)


class EmptyLikelihoodNoCov(Likelihood):
    """Empty mock likelihood that returns None for covariance."""
    def __init__(self):
        self.nothing = 1.0
        self._data_vector = np.array([1.0, 2.0, 3.0])
        super().__init__()

    def read(self, sacc_data: sacc.Sacc):
        pass

    def compute_loglike(self, ModellingTools):
        return -self.nothing*2.0

    def compute_theory_vector(self, ModellingTools):
        return self.nothing

    def get_data_vector(self):
        return self._data_vector

    def get_cov(self):
        return None


def test_verify_sacc_consistency_none_covariance():
    # Create mock inputs where user has None covariance but likelihood has one
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    # Explicitly set covariance to None
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.covariance = None

    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Create a mock module that has build_likelihood returning EmptyLikelihoodNoCov
    # (which returns None for covariance, so __init__ will succeed)
    # Must accept build_parameters argument as required by _test_likelihood
    mock_module = types.ModuleType("mock_likelihood")
    mock_module.build_likelihood = lambda bp: (EmptyLikelihoodNoCov(), ModelingTools())

    smokescreen = ConcealDataVector(cosmo, mock_module,
                                    shifts_dict, sacc_data, systematics_dict)

    # Test that ValueError is raised when user has None but likelihood has covariance
    # Use a mock likelihood with covariance (different from the one used in __init__)
    mock_likelihood = MagicMock()
    mock_likelihood.get_data_vector.return_value = np.array([1.0, 2.0, 3.0])
    mock_likelihood.get_cov.return_value = np.eye(3) * 0.1

    with pytest.raises(ValueError) as exc_info:
        smokescreen._verify_sacc_consistency(mock_likelihood)

    assert "Likelihood has covariance but user-provided SACC" in str(exc_info.value)


def test_verify_sacc_consistency_none_covariance_reverse():
    # Create mock inputs where user has covariance but likelihood returns None
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Add a proper covariance to the SACC object
    n_data = 3
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(n_data) * 0.1)

    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

    # Create a mock likelihood that returns None for covariance
    mock_likelihood = MagicMock()
    mock_likelihood.get_data_vector.return_value = np.array([1.0, 2.0, 3.0])
    mock_likelihood.get_cov.return_value = None

    # Test that ValueError is raised when likelihood has None but user has covariance
    with pytest.raises(ValueError) as exc_info:
        smokescreen._verify_sacc_consistency(mock_likelihood)

    assert "User-provided SACC has covariance but likelihood returns None for covariance." in str(exc_info.value)


def test_debug_mode(capfd):
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    np.testing.assert_array_equal(concealed_data_vector, expected_concealed)


def test_apply_concealing_to_likelihood_datavec_mult():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    np.testing.assert_array_equal(concealed_data_vector, expected_concealing)


def test_apply_concealing_to_likelihood_datavec_invalid_type():
    # Create mock inputs
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    # Add a misc tracer and data points to set up the SACC object properly
    sacc_data.add_tracer('misc', 'test')
    n_data = 3
    for i in range(n_data):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    # Set mean to match EmptyLikelihood's get_data_vector() return value
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)
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
    # Create mock inputs using a 3-element SACC file to match EmptyLikelihood
    cosmo = COSMO
    sacc_data = sacc.Sacc()
    sacc_data.add_tracer('misc', 'test')
    for i in range(3):
        sacc_data.add_data_point('galaxy_shear_cl_ee', ('test', 'test'), 1.0, ell=10)
    sacc_data.mean = np.array([1.0, 2.0, 3.0])
    sacc_data.add_covariance(np.eye(3) * 0.1)

    likelihood = MockLikelihoodModule("mock_likelihood")
    systematics_dict = {"systematic1": 0.1}
    shifts_dict = {"Omega_c": 1}

    # Create Smokescreen instance (this works because data vectors match)
    smokescreen = ConcealDataVector(cosmo, likelihood,
                                    shifts_dict, sacc_data, systematics_dict)

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
def test_save_concealed_datavector(mock_getuser, cosmic_shear_resources, tmp_path):
    # Create mock inputs using fixture resources
    cosmo = COSMO
    likelihood = cosmic_shear_resources['likelihood']
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}
    sacc_data = sacc.Sacc.load_fits(cosmic_shear_resources['fits_sacc'])
    sck = ConcealDataVector(cosmo, likelihood,
                            shift_dict, sacc_data, syst_dict, seed=1234)

    # Calculate the concealing factor and apply it to the likelihood data vector
    sck.calculate_concealing_factor()
    blinded_dv = sck.apply_concealing_to_likelihood_datavec()

    # Save the blinded data vector to a temporary file in tmp_path
    temp_file_path = str(tmp_path)
    temp_file_root = "temp_sacc"
    temp_file_name = f"{temp_file_path}/{temp_file_root}_concealed_data_vector.fits"
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
    # File cleanup handled by tmp_path context manager


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector_hdf5(mock_getuser):
    # Create mock inputs using an HDF5 SACC file to ensure input_format is 'hdf5'
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}

    # Load from HDF5 source
    sacc_data = sacc.Sacc.load_hdf5("./examples/cosmic_shear/cosmicshear_sacc.hdf5")

    # Create ConcealDataVector with input_format='hdf5'
    sck = ConcealDataVector(cosmo, likelihood,
                            shift_dict, sacc_data, syst_dict, seed=1234,
                            **{'input_format': 'hdf5'})

    # Calculate the concealing factor and apply it to the likelihood data vector
    sck.calculate_concealing_factor()
    blinded_dv = sck.apply_concealing_to_likelihood_datavec()

    # Save the blinded data vector to a temporary HDF5 file
    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc_hdf5"
    temp_file_name = f"{temp_file_path}{temp_file_root}_concealed_data_vector.hdf5"

    # Save with output_format='hdf5' to test HDF5 output
    returned_sacc = sck.save_concealed_datavector(temp_file_path,
                                                  temp_file_root,
                                                  return_sacc=True,
                                                  output_format='hdf5')

    # Check that the return is a sacc object
    assert isinstance(returned_sacc, sacc.Sacc)

    # Check that the file was created with .hdf5 extension
    assert os.path.exists(temp_file_name)
    # Verify it's an HDF5 file by checking extension in path
    assert temp_file_name.endswith('.hdf5')

    # Load the HDF5 file and check that the data vector matches
    loaded_sacc = sacc.Sacc.load_hdf5(temp_file_name)
    np.testing.assert_array_equal(loaded_sacc.mean, blinded_dv)

    # Check metadata
    info_str = 'Concealed (blinded) data-vector, created by Smokescreen.'
    assert loaded_sacc.metadata['concealed'] is True
    assert loaded_sacc.metadata['creator'] == mock_getuser.return_value
    assert loaded_sacc.metadata['info'] == info_str

    # Clean up the temporary file
    os.remove(temp_file_name)


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector_hdf5_from_fits_input(mock_getuser):
    # Test that when input format is FITS but output format is explicitly set to HDF5,
    # the file is saved with .hdf5 extension
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}

    # Load from FITS source
    sacc_data = sacc.Sacc.load_fits("./examples/cosmic_shear/cosmicshear_sacc.fits")

    # Create ConcealDataVector with input_format='fits'
    sck = ConcealDataVector(cosmo, likelihood,
                            shift_dict, sacc_data, syst_dict, seed=1234,
                            **{'input_format': 'fits'})

    # Calculate the concealing factor and apply it
    sck.calculate_concealing_factor()
    blinded_dv = sck.apply_concealing_to_likelihood_datavec()

    # Save with explicit HDF5 output format
    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc_hdf5_from_fits"
    temp_file_name = f"{temp_file_path}{temp_file_root}_concealed_data_vector.hdf5"

    returned_sacc = sck.save_concealed_datavector(temp_file_path,
                                                  temp_file_root,
                                                  return_sacc=True,
                                                  output_format='hdf5')

    assert isinstance(returned_sacc, sacc.Sacc)
    assert os.path.exists(temp_file_name)

    # Verify it can be loaded as HDF5
    loaded_sacc = sacc.Sacc.load_hdf5(temp_file_name)
    np.testing.assert_array_equal(loaded_sacc.mean, blinded_dv)

    os.remove(temp_file_name)


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector_default_format_uses_input_format(mock_getuser):
    # Test that when output_format is not specified, it defaults to input format
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}

    # Test with HDF5 input - output should also be HDF5 (.hdf5)
    sacc_data_hdf5, _ = load_sacc_file("./examples/cosmic_shear/cosmicshear_sacc.hdf5")
    sck = ConcealDataVector(cosmo, likelihood,
                            shift_dict, sacc_data_hdf5, syst_dict, seed=1234)

    sck.calculate_concealing_factor()
    blinded_dv = sck.apply_concealing_to_likelihood_datavec()

    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc_default_hdf5"

    # Don't specify output_format - should use input format (hdf5)
    returned_sacc = sck.save_concealed_datavector(temp_file_path,
                                                  temp_file_root,
                                                  return_sacc=True)

    assert isinstance(returned_sacc, sacc.Sacc)

    # Check that the file has .hdf5 extension (from HDF5 input format)
    expected_hdf5_name = f"{temp_file_path}{temp_file_root}_concealed_data_vector.hdf5"
    assert os.path.exists(expected_hdf5_name)

    # Verify it can be loaded as HDF5
    loaded_sacc = sacc.Sacc.load_hdf5(expected_hdf5_name)
    np.testing.assert_array_equal(loaded_sacc.mean, blinded_dv)

    os.remove(expected_hdf5_name)


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector_custom_suffix(mock_getuser):
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}
    sacc_data, _ = load_sacc_file("./examples/cosmic_shear/cosmicshear_sacc.fits")
    sck = ConcealDataVector(cosmo, likelihood, shift_dict, sacc_data, syst_dict, seed=1234)
    sck.calculate_concealing_factor()
    sck.apply_concealing_to_likelihood_datavec()

    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc_custom_suffix"

    sck.save_concealed_datavector(temp_file_path, temp_file_root, suffix="my_blind")

    expected_path = f"{temp_file_path}{temp_file_root}_my_blind.fits"
    default_path = f"{temp_file_path}{temp_file_root}_concealed_data_vector.fits"

    assert os.path.exists(expected_path)
    assert not os.path.exists(default_path)

    os.remove(expected_path)


@patch('src.smokescreen.datavector.getpass.getuser', return_value='test_user')
def test_save_concealed_datavector_default_suffix(mock_getuser):
    cosmo = COSMO
    likelihood = "./examples/cosmic_shear/cosmicshear_likelihood.py"
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    shift_dict = {"Omega_c": 0.34, "sigma8": 0.85}
    sacc_data, _ = load_sacc_file("./examples/cosmic_shear/cosmicshear_sacc.fits")
    sck = ConcealDataVector(cosmo, likelihood, shift_dict, sacc_data, syst_dict, seed=1234)
    sck.calculate_concealing_factor()
    sck.apply_concealing_to_likelihood_datavec()

    temp_file_path = "./tests/"
    temp_file_root = "temp_sacc_default_suffix"

    sck.save_concealed_datavector(temp_file_path, temp_file_root)

    expected_path = f"{temp_file_path}{temp_file_root}_concealed_data_vector.fits"
    assert os.path.exists(expected_path)

    os.remove(expected_path)


def test_flat_distribution_and_deterministic_blinding_equivalence(cosmic_shear_resources):
    """
    Test that blinding from a flat distribution with a given seed produces the same
    data vector as blinding deterministically with the registered sampled shifts.
    """
    cosmo = COSMO
    likelihood = cosmic_shear_resources['likelihood']
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    seed = 1234
    # Distribution-based shifts: sample Omega_c and sigma8 from uniform ranges
    distribution_shifts_dict = {"Omega_c": (0.20, 0.39), "sigma8": (0.6, 0.9)}

    # Step 1: Create smokescreen with distribution-based shifts and get blinded data vector
    sacc_data = sacc.Sacc.load_fits(cosmic_shear_resources['fits_sacc'])
    sck_distribution = ConcealDataVector(cosmo, likelihood,
                                         distribution_shifts_dict, sacc_data,
                                         syst_dict, seed=seed)
    sck_distribution.calculate_concealing_factor()
    blinded_dv_distribution = sck_distribution.apply_concealing_to_likelihood_datavec()

    # Step 2: Register the sampled shift values by re-running the draw with the same seed
    sampled_shifts = sck_distribution._load_shifts(seed=seed)

    # Step 3: Create smokescreen with deterministic shifts equal to the registered sample values
    sacc_data2 = sacc.Sacc.load_fits(cosmic_shear_resources['fits_sacc'])
    sck_deterministic = ConcealDataVector(cosmo, likelihood,
                                          sampled_shifts, sacc_data2,
                                          syst_dict, seed=seed)
    sck_deterministic.calculate_concealing_factor()
    blinded_dv_deterministic = sck_deterministic.apply_concealing_to_likelihood_datavec()

    # Step 4: Both strategies must produce the same blinded data vector
    np.testing.assert_array_almost_equal(blinded_dv_distribution, blinded_dv_deterministic)


def test_gaussian_distribution_and_deterministic_blinding_equivalence(cosmic_shear_resources):
    """
    Test that blinding from a Gaussian distribution with a given seed produces the same
    data vector as blinding deterministically with the registered sampled shifts.
    """
    cosmo = COSMO
    likelihood = cosmic_shear_resources['likelihood']
    syst_dict = {
        "trc1_delta_z": 0.1,
        "trc0_delta_z": 0.1,
    }
    seed = 1234
    # Gaussian distribution shifts: (mean, std) tuples
    distribution_shifts_dict = {"Omega_c": (0.3, 0.02), "sigma8": (0.82, 0.02)}

    # Step 1: Create smokescreen with Gaussian distribution shifts and get blinded data vector
    sacc_data = sacc.Sacc.load_fits(cosmic_shear_resources['fits_sacc'])
    sck_distribution = ConcealDataVector(cosmo, likelihood,
                                         distribution_shifts_dict, sacc_data,
                                         syst_dict, seed=seed,
                                         **{'shift_distr': 'gaussian'})
    sck_distribution.calculate_concealing_factor()
    blinded_dv_distribution = sck_distribution.apply_concealing_to_likelihood_datavec()

    # Step 2: Register the sampled shift values by re-running the Gaussian draw with the same seed
    sampled_shifts = sck_distribution._load_shifts(seed=seed, shift_distr='gaussian')

    # Step 3: Create smokescreen with deterministic shifts equal to the registered sample values
    sacc_data2 = sacc.Sacc.load_fits(cosmic_shear_resources['fits_sacc'])
    sck_deterministic = ConcealDataVector(cosmo, likelihood,
                                          sampled_shifts, sacc_data2,
                                          syst_dict, seed=seed)
    sck_deterministic.calculate_concealing_factor()
    blinded_dv_deterministic = sck_deterministic.apply_concealing_to_likelihood_datavec()

    # Step 4: Both strategies must produce the same blinded data vector
    np.testing.assert_array_almost_equal(blinded_dv_distribution, blinded_dv_deterministic)