import pytest  # noqa: F401
from unittest.mock import patch, MagicMock
from pyccl import CosmologyVanillaLCDM
from smokescreen.utils import load_cosmology_from_partial_dict
from smokescreen import __main__


@patch('builtins.print')
@patch('smokescreen.__main__.ConcealDataVector')
@patch('sacc.Sacc.load_fits')
def test_main(mock_load_fits, mock_smokescreen, mock_print):
    # Arrange
    path_to_sacc = "./examples/cosmic_shear/cosmicshear_sacc.fits"
    likelihood_path = "./tests/test_data/mock_likelihood.py"
    systematics = {}
    shifts_dict = {"Omega_c": [-0.1, 0.2], "sigma8": [-0.1, 0.1]}
    shift_type = 'add'
    seed = 2112
    reference_cosmology = CosmologyVanillaLCDM()
    path_to_output = "./test_data/test_output.fits"

    mock_smokescreen_instance = MagicMock()
    mock_smokescreen.return_value = mock_smokescreen_instance

    sacc_file = MagicMock()  # Create a mock sacc_file
    mock_load_fits.return_value = sacc_file  # Make load_fits return the mock sacc_file

    # Act
    __main__.main(path_to_sacc, likelihood_path, systematics, shifts_dict,
                  shift_type, seed, reference_cosmology, path_to_output)

    # Assert
    mock_load_fits.assert_called_once_with(path_to_sacc)
    mock_smokescreen.assert_called_once_with(reference_cosmology, systematics,
                                             likelihood_path, shifts_dict, sacc_file, seed)
    mock_smokescreen_instance.calculate_concealing_factor.assert_called_once()
    mock_smokescreen_instance.apply_concealing_to_likelihood_datavec.assert_called_once()
    mock_smokescreen_instance.save_concealed_datavector.assert_called_once()


@patch('builtins.print')
@patch('smokescreen.__main__.ConcealDataVector')
@patch('sacc.Sacc.load_fits')
def test_main_loads_cosmology_from_dict(mock_load_fits, mock_smokescreen, mock_print):
    # Arrange
    path_to_sacc = "./examples/cosmic_shear/cosmicshear_sacc.fits"
    likelihood_path = "./tests/test_data/mock_likelihood.py"
    systematics = {}
    shifts_dict = {"Omega_c": [-0.1, 0.2], "sigma8": [-0.1, 0.1]}
    shift_type = 'add'
    seed = 2112
    reference_cosmology = {'sigma8': 0.888}
    path_to_output = "./test_data/test_output.fits"

    mock_smokescreen_instance = MagicMock()
    mock_smokescreen.return_value = mock_smokescreen_instance

    sacc_file = MagicMock()  # Create a mock sacc_file
    mock_load_fits.return_value = sacc_file  # Make load_fits return the mock sacc_file

    # Act
    __main__.main(path_to_sacc, likelihood_path, systematics, shifts_dict, shift_type,
                  seed, reference_cosmology, path_to_output)

    # Assert
    mod_ref_cosmo = load_cosmology_from_partial_dict(reference_cosmology)
    mock_load_fits.assert_called_once_with(path_to_sacc)
    mock_smokescreen.assert_called_once_with(mod_ref_cosmo, systematics,
                                             likelihood_path, shifts_dict, sacc_file, seed)
    mock_smokescreen_instance.calculate_concealing_factor.assert_called_once()
    mock_smokescreen_instance.apply_concealing_to_likelihood_datavec.assert_called_once()
    mock_smokescreen_instance.save_concealed_datavector.assert_called_once()
