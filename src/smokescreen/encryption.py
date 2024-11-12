# author: Arthur Loureiro <arthur.loureiro@fysik.su.se>
# license: BSD 3-Clause
'''
Encryption (:mod:`smokescreen.encryption`)
===================================================

.. currentmodule:: smokescreen.encryption

The :mod:`smokescreen.encryption` module provides functions to encrypt and decrypt files.

Smokescreen Encryption
----------------------
.. autofunction:: encrypt_file
.. autofunction:: decrypt_file
'''

import os
from cryptography.fernet import Fernet


def encrypt_file(path_to_file: str, path_to_save: str = None,
                 save_file: bool = False, keep_original: bool = False) -> bytes:
    """
    Encrypts a SACC file using Fernet encryption.

    Parameters
    ----------
    path_to_file : str
        Path to the SACC file to be encrypted.
    path_to_save : str, optional
        Path to save the key used to encrypt the file, and the encrypted file.
        by default None [saves in the same directory as the encrypted file].
    save_file : bool, optional
        If True, saves the encrypted file in the same directory
        as the original file, by default False.

    Returns
    -------
    encrypted_sacc : bytes
        Encrypted SACC file.
    key : bytes
        Key used to encrypt the file.
    """
    # check if the file exists:
    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"File {path_to_file} not found")
    # gets the path from the file
    path = os.path.dirname(path_to_file)

    # generate a key
    key = Fernet.generate_key()
    # create a cipher
    cipher = Fernet(key)

    # read the file
    with open(path_to_file, "rb") as file:
        sacc = file.read()

    # encrypt the file
    encrypted_sacc = cipher.encrypt(sacc)

    # save the file
    if save_file:
        if path_to_save is not None:
            # check if the path exists and create it if it does not
            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)
        else:
            path_to_save = path
        # changes the extension of the file to .encrpt
        filename = os.path.basename(path_to_file)
        filename = filename.split(".")[0] + ".encrpt"
        # save the file
        with open(os.path.join(path_to_save, filename), "wb") as file:
            file.write(encrypted_sacc)

        # saves the key in a txt file with the same name and extension .key
        with open(os.path.join(path_to_save, filename.split(".")[0] + ".key"), "wb") as file:
            file.write(key)

    if keep_original is False:
        os.remove(path_to_file)

    return encrypted_sacc, key


def decrypt_file(path_to_file: str, key: str, save_file: bool = False) -> bytes:
    """
    Decrypts a SACC file using Fernet encryption.

    Parameters
    ----------
    path_to_sacc : str
        Path to the SACC file to be decrypted.
    key : str
        path to the file with the key used to encrypt the SACC.
    save_file : bool, optional
        If True, saves the decrypted file in the same directory as the original file,
        by default False.
    """
    # check if the file exists:
    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"File {path_to_file} not found")
    # gets the path from the file
    path = os.path.dirname(path_to_file)

    # check if the key exists:
    if not os.path.exists(key):
        raise FileNotFoundError(f"Key {key} not found")
    # read the key
    with open(key, "rb") as file:
        key = file.read()

    # create a cipher
    cipher = Fernet(key)

    # read the file
    with open(path_to_file, "rb") as file:
        sacc = file.read()

    # decrypt the file
    decrypted_sacc = cipher.decrypt(sacc)

    # save the file
    if save_file:
        # changes the extension of the file to .dec
        filename = os.path.basename(path_to_file)
        filename = filename.split(".")[0] + ".fits"
        # save the file
        with open(os.path.join(path, filename), "wb") as file:
            file.write(decrypted_sacc)

    return decrypted_sacc
