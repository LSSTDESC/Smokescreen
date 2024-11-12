import os
import pytest
from smokescreen.encryption import encrypt_file, decrypt_file


@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    with open(file_path, "w") as f:
        f.write("This is a test file.")
    return file_path


def test_encrypt_file(temp_file):
    # Test encrypting a file without saving the encrypted file
    encrypted_sacc, key = encrypt_file(str(temp_file))
    assert isinstance(encrypted_sacc, bytes)
    assert isinstance(key, bytes)


def test_encrypt_file_save(temp_file, tmp_path):
    # Test encrypting a file and saving the encrypted file
    path_to_save = tmp_path / "encrypted"
    encrypted_sacc, key = encrypt_file(str(temp_file),
                                       path_to_save=str(path_to_save),
                                       save_file=True)
    assert isinstance(encrypted_sacc, bytes)
    assert isinstance(key, bytes)

    # Check if the encrypted file and key file are saved
    encrypted_file_path = path_to_save / "test_file.encrpt"
    key_file_path = path_to_save / "test_file.key"
    assert os.path.exists(encrypted_file_path)
    assert os.path.exists(key_file_path)

    # Check if the content of the key file is correct
    with open(key_file_path, "rb") as f:
        saved_key = f.read()
    assert saved_key == key


def test_encrypt_file_keep_original(temp_file):
    # Test encrypting a file and keeping the original file
    encrypted_sacc, key = encrypt_file(str(temp_file), save_file=True, keep_original=True)
    assert isinstance(encrypted_sacc, bytes)
    assert isinstance(key, bytes)

    # Check if the original file still exists
    assert os.path.exists(temp_file)


def test_encrypt_file_remove_original(temp_file):
    # Test encrypting a file and removing the original file
    encrypted_sacc, key = encrypt_file(str(temp_file), save_file=True, keep_original=False)
    assert isinstance(encrypted_sacc, bytes)
    assert isinstance(key, bytes)

    # Check if the original file is removed
    assert not os.path.exists(temp_file)


def test_encrypt_file_nonexistent():
    # Test encrypting a nonexistent file
    with pytest.raises(FileNotFoundError):
        encrypt_file("nonexistent_file.txt")


@pytest.fixture
def encrypted_file_and_key(temp_file, tmp_path):
    path_to_save = tmp_path / "encrypted"
    encrypted_sacc, key = encrypt_file(str(temp_file),
                                       path_to_save=str(path_to_save),
                                       save_file=True)
    encrypted_file_path = path_to_save / "test_file.encrpt"
    key_file_path = path_to_save / "test_file.key"
    return encrypted_file_path, key_file_path


def test_decrypt_file(encrypted_file_and_key):
    encrypted_file_path, key_file_path = encrypted_file_and_key

    # Test decrypting the file
    decrypted_sacc = decrypt_file(str(encrypted_file_path), str(key_file_path))
    assert isinstance(decrypted_sacc, bytes)
    assert decrypted_sacc == b"This is a test file."


def test_decrypt_file_save(encrypted_file_and_key, tmp_path):
    encrypted_file_path, key_file_path = encrypted_file_and_key

    # Test decrypting the file and saving the decrypted file
    decrypted_sacc = decrypt_file(str(encrypted_file_path),
                                  str(key_file_path),
                                  save_file=True)
    assert isinstance(decrypted_sacc, bytes)
    assert decrypted_sacc == b"This is a test file."

    # Check if the decrypted file is saved
    decrypted_file_path = tmp_path / "encrypted" / "test_file.fits"
    assert os.path.exists(decrypted_file_path)

    # Check if the content of the decrypted file is correct
    with open(decrypted_file_path, "rb") as f:
        saved_decrypted_sacc = f.read()
    assert saved_decrypted_sacc == b"This is a test file."


def test_decrypt_file_nonexistent():
    # Test decrypting a nonexistent file
    with pytest.raises(FileNotFoundError):
        decrypt_file("nonexistent_file.encrpt", "nonexistent_key.key")


def test_decrypt_file_nonexistent_key(encrypted_file_and_key):
    encrypted_file_path, _ = encrypted_file_and_key

    # Test decrypting with a nonexistent key
    with pytest.raises(FileNotFoundError):
        decrypt_file(str(encrypted_file_path), "nonexistent_key.key")
