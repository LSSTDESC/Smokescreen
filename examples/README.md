# Examples
This directory contains examples on how to build a firecrown likelihood that could be used to to blind datavectors. 

These need to contain the following methods:
- `build_likelihood` which returns a `firecrown.Likelihood` object
- `.compute_theory_vector(ModellingTools)` which returns the theory vector for the given model
- `.get_data_vector()` which returns the data vector from the likelihood

There should also be a way for providing a SACC file to the likelihood externally. This can be done by adding a `sacc_file` argument to the `build_likelihood` method via the `build_params` dictionary.

## Cosmic Shear Example
The cosmic shear example here is based on the example provided in the [firecrown repository](https://github.com/LSSTDESC/firecrown/blob/master/examples/cosmicshear/cosmicshear.py). 

The data-vector, `cosmicshear_sacc.fits`, was computed using the `generate_cosmicshear_data.py` script in the [firecrown examples directory](https://github.com/LSSTDESC/firecrown/blob/master/examples/cosmicshear/generate_cosmicshear_data.py).