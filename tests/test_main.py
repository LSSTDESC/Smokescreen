import pytest  # noqa: F401
import os
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet
from pyccl import CosmologyVanillaLCDM
from smokescreen.utils import load_cosmology_from_partial_dict
from smokescreen import __main__
from smokescreen.__main__ import encrypt_main, decrypt_main


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
    shift_distribution = 'flat'
    seed = 2112
    reference_cosmology = CosmologyVanillaLCDM()
    path_to_output = "./tests/test_data/"
    keep_original_sacc = True

    mock_smokescreen_instance = MagicMock()
    mock_smokescreen.return_value = mock_smokescreen_instance

    sacc_file = MagicMock()  # Create a mock sacc_file
    mock_load_fits.return_value = sacc_file  # Make load_fits return the mock sacc_file

    # Act
    __main__.datavector_main(path_to_sacc, likelihood_path, shifts_dict, systematics,
                             shift_type, shift_distribution, seed, reference_cosmology,
                             path_to_output, keep_original_sacc)

    # Assert
    mock_load_fits.assert_called_once_with(path_to_sacc)
    mock_smokescreen.assert_called_once_with(reference_cosmology, likelihood_path,
                                             shifts_dict, sacc_file, systematics, seed,
                                             shift_distr=shift_distribution)
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
    shift_distribution = 'flat'
    seed = 2112
    reference_cosmology = {'sigma8': 0.888}
    path_to_output = "./tests/test_data/"
    keep_original_sacc = True

    mock_smokescreen_instance = MagicMock()
    mock_smokescreen.return_value = mock_smokescreen_instance

    sacc_file = MagicMock()  # Create a mock sacc_file
    mock_load_fits.return_value = sacc_file  # Make load_fits return the mock sacc_file

    # Act
    __main__.datavector_main(path_to_sacc, likelihood_path, shifts_dict, systematics, shift_type,
                             shift_distribution, seed, reference_cosmology,
                             path_to_output, keep_original_sacc)

    # Assert
    mod_ref_cosmo = load_cosmology_from_partial_dict(reference_cosmology)
    mock_load_fits.assert_called_once_with(path_to_sacc)
    mock_smokescreen.assert_called_once_with(mod_ref_cosmo, likelihood_path, shifts_dict,
                                             sacc_file, systematics, seed,
                                             shift_distr=shift_distribution)
    mock_smokescreen_instance.calculate_concealing_factor.assert_called_once()
    mock_smokescreen_instance.apply_concealing_to_likelihood_datavec.assert_called_once()
    mock_smokescreen_instance.save_concealed_datavector.assert_called_once()


@patch('builtins.print')
@patch('smokescreen.__main__.ConcealDataVector')
@patch('sacc.Sacc.load_fits')
def test_main_gaussian_shift(mock_load_fits, mock_smokescreen, mock_print):
    # Arrange
    path_to_sacc = "./examples/cosmic_shear/cosmicshear_sacc.fits"
    likelihood_path = "./tests/test_data/mock_likelihood.py"
    systematics = {}
    shifts_dict = {"Omega_c": [-0.1, 0.2], "sigma8": [-0.1, 0.1]}
    shift_type = 'add'
    shift_distribution = 'gaussian'
    seed = 2112
    reference_cosmology = CosmologyVanillaLCDM()
    path_to_output = "./tests/test_data/"
    keep_original_sacc = True

    mock_smokescreen_instance = MagicMock()
    mock_smokescreen.return_value = mock_smokescreen_instance

    sacc_file = MagicMock()  # Create a mock sacc_file
    mock_load_fits.return_value = sacc_file  # Make load_fits return the mock sacc_file

    # Act
    __main__.datavector_main(path_to_sacc, likelihood_path, shifts_dict,
                             systematics, shift_type, shift_distribution, seed,
                             reference_cosmology,
                             path_to_output, keep_original_sacc)

    # Assert
    mock_load_fits.assert_called_once_with(path_to_sacc)
    mock_smokescreen.assert_called_once_with(reference_cosmology,
                                             likelihood_path, shifts_dict, sacc_file,
                                             systematics, seed,
                                             shift_distr=shift_distribution)
    mock_smokescreen_instance.calculate_concealing_factor.assert_called_once()
    mock_smokescreen_instance.apply_concealing_to_likelihood_datavec.assert_called_once()
    mock_smokescreen_instance.save_concealed_datavector.assert_called_once()


@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.sacc"
    with open(file_path, "w") as f:
        f.write("This is a test SACC file.")
    return file_path


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path / "output"


@patch('smokescreen.__main__.encrypt_file')
@patch('smokescreen.__main__.getpass.getuser', return_value='test_user')
def test_encrypt_main(mock_getuser, mock_encrypt_file, temp_file, temp_dir, capsys):
    # Mock the encrypt_file function
    mock_encrypt_file.return_value = (b'encrypted_sacc', b'key')

    # Call the encrypt_main function
    encrypt_main(path_to_sacc=str(temp_file), path_to_save=str(temp_dir), keep_original=True)

    # Check if the encrypt_file function was called with the correct parameters
    mock_encrypt_file.assert_called_once_with(str(temp_file),
                                              str(temp_dir), save_file=True,
                                              keep_original=True)

    # Check if the output messages are correct
    captured = capsys.readouterr()
    assert "SACC file" in captured.out
    assert "encrypted successfully" in captured.out
    assert "Key saved as" in captured.out
    assert "Encrypted file saved as" in captured.out
    assert "Original file" not in captured.out


@patch('smokescreen.__main__.encrypt_file')
@patch('smokescreen.__main__.getpass.getuser', return_value='test_user')
def test_encrypt_main_remove_original(mock_getuser, mock_encrypt_file, temp_file, temp_dir, capsys):
    # Mock the encrypt_file function
    mock_encrypt_file.return_value = (b'encrypted_sacc', b'key')

    # Call the encrypt_main function
    encrypt_main(path_to_sacc=str(temp_file), path_to_save=str(temp_dir), keep_original=False)

    # Check if the encrypt_file function was called with the correct parameters
    mock_encrypt_file.assert_called_once_with(str(temp_file),
                                              str(temp_dir),
                                              save_file=True,
                                              keep_original=False)

    # Check if the output messages are correct
    captured = capsys.readouterr()
    assert "SACC file" in captured.out
    assert "encrypted successfully" in captured.out
    assert "Key saved as" in captured.out
    assert "Encrypted file saved as" in captured.out
    assert "Original file" in captured.out


def test_encrypt_main_file_not_found():
    # Test encrypting a nonexistent file
    with pytest.raises(AssertionError):
        encrypt_main(path_to_sacc="nonexistent_file.sacc")


def test_encrypt_main_no_save_path(temp_file, capsys):
    # Call the encrypt_main function without specifying a save path
    encrypt_main(path_to_sacc=str(temp_file), keep_original=True)

    # Check if the encrypted file and key file are saved in the same directory as the original file
    encrypted_file_path = temp_file.with_suffix('.encrpt')
    key_file_path = temp_file.with_suffix('.key')
    assert os.path.exists(encrypted_file_path)
    assert os.path.exists(key_file_path)

    # Check if the output messages are correct
    captured = capsys.readouterr()
    assert "SACC file" in captured.out
    assert "encrypted successfully" in captured.out
    assert "Key saved as" in captured.out
    assert "Encrypted file saved as" in captured.out
    assert "Original file" not in captured.out


@pytest.fixture
def temp_encrypted_file_and_key(tmp_path):
    # Create a temporary encrypted file and key
    encrypted_file_path = tmp_path / "test_file.encrpt"
    key_file_path = tmp_path / "test_file.key"
    with open(encrypted_file_path, "wb") as f:
        f.write(b"encrypted_sacc")
    with open(key_file_path, "wb") as f:
        f.write(Fernet.generate_key())
    return encrypted_file_path, key_file_path


@patch('smokescreen.__main__.decrypt_file')
@patch('smokescreen.__main__.getpass.getuser', return_value='test_user')
def test_decrypt_main(mock_getuser, mock_decrypt_file, temp_encrypted_file_and_key, capsys):
    encrypted_file_path, key_file_path = temp_encrypted_file_and_key

    # Mock the decrypt_file function
    mock_decrypt_file.return_value = b'decrypted_sacc'

    # Call the decrypt_main function
    decrypt_main(path_to_sacc=str(encrypted_file_path), path_to_key=str(key_file_path))

    # Check if the decrypt_file function was called with the correct parameters
    mock_decrypt_file.assert_called_once_with(str(encrypted_file_path),
                                              str(key_file_path),
                                              save_file=True)

    # Check if the output messages are correct
    captured = capsys.readouterr()
    assert "SACC file" in captured.out
    assert "decrypted successfully" in captured.out
    assert "Decrypted file saved as" in captured.out


def test_decrypt_main_file_not_found():
    # Test decrypting a nonexistent file
    with pytest.raises(AssertionError):
        decrypt_main(path_to_sacc="nonexistent_file.encrpt", path_to_key="nonexistent_key.key")


def test_decrypt_main_key_not_found(temp_encrypted_file_and_key):
    encrypted_file_path, _ = temp_encrypted_file_and_key

    # Test decrypting with a nonexistent key
    with pytest.raises(AssertionError):
        decrypt_main(path_to_sacc=str(encrypted_file_path), path_to_key="nonexistent_key.key")

# def test_decrypt_main_no_save_path(temp_encrypted_file_and_key, capsys):
#     encrypted_file_path, key_file_path = temp_encrypted_file_and_key

#     # Call the decrypt_main function without specifying a save path
#     decrypt_main(path_to_sacc=str(encrypted_file_path), path_to_key=str(key_file_path))

#     # Check if the decrypted file is saved in the same directory as the original file
#     decrypted_file_path = encrypted_file_path.with_suffix('.fits')
#     assert os.path.exists(decrypted_file_path)

#     # Check if the output messages are correct
#     captured = capsys.readouterr()
#     assert "SACC file" in captured.out
#     assert "decrypted successfully" in captured.out
#     assert "Decrypted file saved as" in captured.out
