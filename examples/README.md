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
smokescreen datavector --config blind_cosmic_shear_example.yaml
```

You can find a notebook example on how to run this from the command line at `notebooks/test_cosmicshear_example.ipynb`.

## Supernovae Type Ia
The Supernovae Type Ia example is based on the example provided in the [firecrown repository](https://github.com/LSSTDESC/firecrown/tree/master/examples/srd_sn).

The datavector was also computed from the firecrown example.

You can run this example from the `supernovae/` directory using the following command:
```bash
smokescreen datavector --config blind_sn_example.yaml
```
You can find a notebook example on how to run this from the command line at `notebooks/test_supernova_example.ipynb`.

## LSST Y1 3x2pt Example
> __:warning: Important: this folder contains the example used in the Smokescreen JOSS paper__
>
> :pushpin: The 3x2pt LSST Y1 SACC file here (`sacc_forecasting_y1_3x2pt.sacc`) was produced by Pedro H. Ribeiro ( @Arara09 ) as a part of DESC Project 314, if you intend to use this for another project, please give credit to him. 

This folder contains the deterministic concealment on $(A_s, w)$-space of a LSST Y1 3x2pt sacc forecasted data vector. The shifts are determinist as this folder is a proof of concept used in the Smokescreen JOSS Paper.

The fiducial cosmology used to generate this sacc is:
```yaml
Omega_c = 0.2906682
Omega_b = 0.04575
A_s_1e9 = 1.9019
n_s = 0.9493
h0 = 0.6714
w = -3.0 -1.0 0.0
wa = 0.0
mnu = 0.1
nnu = 3.044
TCMB = 2.7255
Omega_k = 0.0
num_massive_neutrinos = 3
tau = 0.0544
```

There are two concealment smokescreen files here:
* **Blind A**: Shifts $A_s \rightarrow 2.00\times 10^{-09}$ and $w\rightarrow -1.1$
* **Blind B**: Shifts $A_s \rightarrow 1.80\times 10^{-09}$ and $w\rightarrow -0.9$

You can run these examples with:
```bash
smokescreen datavector --config conceal_lsst_y1_3x2pt_blind_[A/B].yaml
```

### Cosmosis files
The folder `lsst_3x2pt/cosmosis_ini_files` also contains the cosmosis files to reproduce the posteriors shown in the Smokescreen JOSS paper. Cosmosis will vary only these three cosmological paramters $(A_s, \Omega_{\rm cdm}, w)$ for the example.

The `.ini` files are:
* `cosmosis_lsst_3x2pt.ini`: the run without concealment.
* `cosmosis_lsst_3x2pt_blind_A.ini`: the blind A case.
* `cosmosis_lsst_3x2pt_blind_B.ini`: the blind B case.

**Please note: you may need to change the `project_dir` variable in the `.ini` files to the folder where your copy of smokescreen is located.**