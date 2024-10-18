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
    # only needed if you want a different reference cosmology
    # than ccl.VanillaLCDM
    reference_cosmology: 
        sigma8: 0.85

Or you can use the following command to create a template configuration file:

.. code-block:: bash

   python -m smokescreen --print_config > template_config.yaml

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
   smoke = ConcealDataVector(cosmo, syst_dict, sacc_data, my_likelihood, 
                             {'Omega_c': (0.22, 0.32), 'sigma8': (0.7, 0.9)})
   # conceals (blinds) the data vector
   smoke.calculate_concealing_factor()
   concealed_dv = smoke.apply_concealing_to_likelihood_datavec()

Encryption and Decryption
-------------------------

The `Smokescreen` library now includes functionality to encrypt and decrypt the SACC files to avoid accidental unblinding.

To encrypt the SACC file before saving it to disk, the `save_concealed_datavector` method in the `ConcealDataVector` class has been updated. The method now generates an encryption key, encrypts the SACC data, and saves the encrypted data along with the encryption key in separate files.

To decrypt the SACC file, you can use the `decrypt_sacc_file` function provided in the `smokescreen.datavector` module. This function uses the saved encryption key to decrypt the SACC file.

Example usage:

.. code-block:: python

   from smokescreen.datavector import decrypt_sacc_file

   # Path to the encrypted SACC file and the encryption key file
   encrypted_sacc_path = "path/to/encrypted_sacc_file.fits"
   encryption_key_path = "path/to/encryption_key.txt"

   # Decrypt the SACC file
   decrypted_sacc = decrypt_sacc_file(encrypted_sacc_path, encryption_key_path)

   # Now you can use the decrypted SACC file as needed
   print(decrypted_sacc)
