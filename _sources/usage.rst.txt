Usage
======

Currently, only data vector concealment is implemented in Smokescreen. Posterior-level concealment is under development.

Data Vector Concealment (blinding)
-----------------------------------

The `Smokescreen` library provides a method for blinding data vectors. This method is based on the `Muir et al. (2021) <https://arxiv.org/abs/1911.05929>`_ data-vector blinding method.

To conceal a data-vector you need the following elements:

* A CCL cosmology object

* A dictionary of the nuisance parameters used in the likelihood (soon to be deprecated)

* A Firecrown Likelihood, which takes a SACC data-vector (see more below). It can be either a path to the python file containing the likelihood or the module itself.

* A dictionary of cosmological parameters to be shifted in the format:
    
      .. code-block:: python

        # for a random uniform parameter shift:
        {'PARAM_Y': (Y_MIN, Y_MAX), 'PARAM_Z': (Z_MIN, Z_MAX)}
        # or for a determinist shift (used for debugging):
        {'PARAM_Y': Y_VALUE, 'PARAM_Z': Z_VALUE}

        # for a Gaussian parameter shift:
        {'PARAM_Y': (MEAN_Y, STD_Y), 'PARAM_Z': (MEAN_Z, STD_Z)}

* A SACC data-vector

* A random seed as int or string

.. attention::
   **Likelihood Requirements**

   The blinding module requires the Firecrown likelihood to be built with certain requirements. First, we must be able to build the likelihood by providing a `sacc <https://github.com/LSSTDESC/sacc/tree/master>`_ object with the measurements for the data-vector:

    .. code-block:: python

        def build_likelihood(build_parameters):
            """
            This is a generic likelihood theory model 
            for a generic data vector.
            """
            sacc_data = build_parameters['sacc_data']

    This is simular to what is currently done in `TXPipe <https://github.com/LSSTDESC/TXPipe/blob/df0dcc8c1e974576dd1942624ab5ff7bd0fbbaa0/txpipe/utils/theory_model.py#L19>`_.

    The likelihood module also must have a method ``.compute_theory_vector(ModellingTools)`` which calls for the calculation of the theory vector inside the likelihood object. 

.. danger::
    **Likelihoods with hardcoded sacc files:**

    If you provide a Firecrown likelihood with a hardcoded path to a sacc file as the data-vector, **Smokescreen will conceal the hardcoded sacc file and not the one you provided**. This is because the likelihood is built with the hardcoded path. Firecrown currently has not checks to avoid a hardcoded sacc file in the ``build_likelihood(...)`` function. To avoid this, please build the likelihood as described above.

The likelihood can be provided either as a path to the python file containing the ``build_likelihood`` function or as a python module. In the latter case, the module must be imported.

TL;DR: Check the `Smokescreen notebooks folder <https://github.com/LSSTDESC/Smokescreen/tree/main/notebooks>`_ for a couple of examples.

From the command line
~~~~~~~~~~~~~~~~~~~~~~
The blinding module can be used to blind the data-vector measurements. The module can be used as follows:

.. code-block:: bash

   python -m smokescreen --config configuration_file.yaml

From Smokescreen version 1.3.0 you should call the module as:

.. code-block:: bash

   smokescreen datavector --config configuration_file.yaml

You can find an example of a configuration file here: 

.. code-block:: yaml

    path_to_sacc: "./cosmicshear_sacc.fits"
    likelihood_path: "./cosmicshear_likelihood.py"
    systematics:
        trc1_delta_z: 0.1
        trc0_delta_z: 0.1
    shifts_dict:
        Omega_c: [0.20, 0.42]
        sigma8: [0.67, 0.92]
    seed: 2112
    shift_distribution: "flat"
    # only needed if you want a different reference cosmology
    # than ccl.VanillaLCDM
    reference_cosmology: 
        sigma8: 0.85
    keep_original_sacc: true

.. note::

    **As of version 1.5.0 of Smokescreen, you no longer need to provide the `systematics` dictionary in the configuration file. The module will automatically extract the systematics from the firecrown likelihood's default values. Of course, you can still provide this dictionary if you want values different than the firecrown defaults**

.. warning::

    **By default, the original SACC file is deleted after the encryption. If you want to keep the original SACC file, you can set the `keep_original_sacc` parameter to `true` in the configuration file.**

Or you can use the following command to create a template configuration file:

.. code-block:: bash

   python -m smokescreen --print_config > template_config.yaml
   # or in version 1.3.0+
   smokescreen datavector --print_config > template_config.yaml

Note that the `reference_cosmology` is optional. If not provided, the CCL `VanillaLCDM` reference cosmology will be the one used to compute the data vector.

From a notebook/your code
~~~~~~~~~~~~~~~~~~~~~~~~~

The smokescreen module can be used to blind the data-vector measurements. The module can be used as follows:

.. code-block:: python

   # import the module
   import pyccl as ccl
   from smokescreen import ConcealDataVector
   # import the likelihood that contains the model and data vector
   [...]
   import my_likelihood

   # create the cosmology ccl object
   cosmo = ccl.Cosmology(Omega_c=0.27, 
                         Omega_b=0.045, 
                         h=0.67, 
                         sigma8=0.8, 
                         n_s=0.96, 
                         transfer_function='bbks')
   # load a sacc object with the data vector [FIXME: this is a placeholder, the sacc object should be loaded from the likelihood]
   sacc_data = sacc.Sacc.load_fits('path/to/data_vector.sacc')
   # create a dictionary of the necessary firecrown nuisance parameters
   # from version 1.5.0 of Smokescreen, the systematics dictionary can be optional (more info above)
   syst_dict = {
               "ia_a_1": 1.0,
               "ia_a_2": 0.5,
               "ia_a_d": 0.5,
               "lens0_bias": 2.0,
               "lens0_b_2": 1.0,
               "lens0_b_s": 1.0,
               "lens0_mag_bias": 1.0,
               "src0_delta_z": 0.000,
               "lens0_delta_z": 0.000,}
   # create the smokescreen object
   smoke = ConcealDataVector(cosmo, sacc_data, my_likelihood, 
                             {'Omega_c': (0.22, 0.32), 'sigma8': (0.7, 0.9)},
                             syst_dict, 
                             shift_distr='flat')
   # conceals (blinds) the data vector
   smoke.calculate_concealing_factor()
   concealed_dv = smoke.apply_concealing_to_likelihood_datavec()

   # create the smokescreen object with Gaussian shifts
   smoke_gaussian = ConcealDataVector(cosmo, syst_dict, sacc_data, my_likelihood, 
                                      {'Omega_c': (0.27, 0.05), 'sigma8': (0.8, 0.02)}, shift_distr='gaussian')
   # conceals (blinds) the data vector with Gaussian shifts
   smoke_gaussian.calculate_concealing_factor()
   concealed_dv_gaussian = smoke_gaussian.apply_concealing_to_likelihood_datavec()

To encrypt the original sacc file, follow the instructions in the next section.

Encryting and Decrypting SACC files
------------------------------------
From Smokescreen version 1.3.0, you can encrypt and decrypt SACC files. This is useful when you want to share the data vector with someone else but you don't want them to see the data. The encryption is done using the `cryptography <https://cryptography.io/en/latest/>`_ library. It is important to note that the encryption is done using a symmetric key, so the person you are sharing the data with must have the key to decrypt the file.

When running the data vector concealment module, encryption is performed by default. The decryption key is saved in a file with the same name as the original file but a `.key` extension. The key is saved in the same directory as the encrypted file.

.. warning::

    **By default, the original SACC file is deleted after the encryption. If you want to keep the original SACC file, you can set the `keep_original_sacc` parameter to `true` in the configuration file or set the flag `--keep_original true` via command line**

Encrypting files
~~~~~~~~~~~~~~~~
To encrypt a sacc file (or any file), you can use the following command:

.. code-block:: bash

   smokescreen encrypt --path_to_sacc path/to/sacc.fits --path_to_save path/to/save/the/file/ [--keep_original true]

This will generate an encrypted file with the extension `.encrpt` and a key file with the extension `.key` in the same directory as the encrypted file or in the directory specified by `--path_to_save`.

You can also encrypt a file from a notebook/your code:

.. code-block:: python

   from smokescreen.encryption import encrypt_sacc
   encrypt_sacc('path/to/sacc.fits', 'path/to/save/the/file/', save_file=True, keep_original=False)

Decrypting files
~~~~~~~~~~~~~~~~
To decrypt the file, you can use the following command:

.. code-block:: bash

   smokescreen decrypt --path_to_sacc [path_to_encrypted_sacc] --path_to_key [path_to_file_with_key]

or from a notebook/your code:

.. code-block:: python

   from smokescreen.encryption import decrypt_sacc
   decrypt_sacc('path/to/encrypted_sacc.encrpt', 'path/to/key.key', save_file=True)

The `save_file` parameter is optional and is set to `True` by default. If set to `False`, the decrypted file will not be saved to disk.


Posterior Concealment (blinding)
---------------------------------

.. warning::

    **UNDER DEVELOPMENT**