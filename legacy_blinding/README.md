# Legacy Cosmosis Blinding for Data-Vectors

This folder contains scripts to implement the [Muir et al. 2020](https://arxiv.org/abs/1911.05929) data-vector blinding scheme.
The package in this folder is a direct adaptation of Jessie Muir's DES Y3 blinding scripts.

## Installation
- Install cosmosis via `conda install -c conda-forge cosmosis`
- Activate the cosmosis configuration via `source cosmosis-configure`
- Install the cosmosis standard library via `conda install -c conda-forge cosmosis-build-standard-library`
- Install the standard library in the correct cosmosis folder `cosmosis-build-standard-library -i`

## Usage
> Don't forget to `source cosmosis-configure`
### Tests
To run the unit tests, go to the `tests/` and run `pytest`

To test main: `python -m blind_2pt_cosmosis -u blind_2pt_cosmosis/cosmosis_files/sim_fiducial.fits --log-level DEBUG`