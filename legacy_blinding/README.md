# Legacy Cosmosis Blinding for 2pt Data-Vectors using Cosmosis

This folder contains an implementation of [Muir et al. 2020](https://arxiv.org/abs/1911.05929) data-vector blinding strategy using Cosmosis V2.
The package in this folder is a direct adaptation of Jessie Muir's DES Y3 blinding scripts to the DESC context.

## Installation
- Install cosmosis via `conda install -c conda-forge cosmosis`
- Activate the cosmosis configuration via `source cosmosis-configure`
- Install the cosmosis standard library via `conda install -c conda-forge cosmosis-build-standard-library`
- Install the standard library in the correct cosmosis folder `cosmosis-build-standard-library -i`

### Legacy Blinding installation 
In the `legacy_blinding/` folder, simply install with 
```bash
python -m pip install -e .
```

### Test the installation
To run the unit tests:
```bash
cd tests
pytest .
```

## Usage
> Don't forget to `source cosmosis-configure`

To get the docstring on the command-line interface:
```
python -m blind_2pt_cosmosis --help
```

To run an example: 
```bash
python -m blind_2pt_cosmosis -u src/blind_2pt_cosmosis/cosmosis_files/sim_fiducial.fits [--log-level DEBUG]
```

[!] Note: You can also include all the command line arguments in a `.config` file and call `python -m blind_2pt_cosmosis @example.config` instead. This will be adapted to use `yaml` files in the near future.