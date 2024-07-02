# Examples
This directory contains examples on how to build a firecrown likelihood that could be used to to blind datavectors. 

These need to contain the following methods:
- `build_likelihood` which returns a tuple with a `firecrown.Likelihood` and a `ModellingTools` object.
- `.compute_theory_vector(ModellingTools)` which returns the theory vector for the given model
- `.get_data_vector()` which returns the data vector from the likelihood

Note that, if you are using a likelihood from Firecrown, both `.compute_theory_vector()` and `.get_data_vector()` are already implemented in the `GaussFamily` base class.

There should also be a way for providing a SACC file to the likelihood externally. This can be done by adding a `sacc_file` argument to the `build_likelihood` method via the `build_params` dictionary.

## Cosmic Shear Example
The cosmic shear example here is based on the example provided in the [firecrown repository](https://github.com/LSSTDESC/firecrown/blob/master/examples/cosmicshear/cosmicshear.py). 

The data-vector, `cosmicshear_sacc.fits`, was computed using the `generate_cosmicshear_data.py` script in the [firecrown examples directory](https://github.com/LSSTDESC/firecrown/blob/master/examples/cosmicshear/generate_cosmicshear_data.py).

You can run this example from `cosmic_shear/` directory using the following command:
```bash
python -m blinding blind_cosmic_shear_example.yaml
```

You can find a notebook example on how to run this from the command line at `notebooks/test_cosmicshear_example.ipynb`.

## Supernovae Type Ia
The Supernovae Type Ia example is based on the example provided in the [firecrown repository](https://github.com/LSSTDESC/firecrown/tree/master/examples/srd_sn).

The datavector was also computed from the firecrown example.

You can run this example from the `supernovae/` directory using the following command:
```bash
python -m blinding blind_sn_example.yaml
```
You can find a notebook example on how to run this from the command line at `notebooks/test_supernova_example.ipynb`.