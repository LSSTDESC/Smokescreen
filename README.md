# DESC Blinding Modules
This repostory (under development) contains the blinding modules for blinding at the following levels of the analysis:
- Data-vector measurements
- Posterior distribution
- (TBC) Catalogues

Other info: the previous README can be found [here](bckp_README.md)

## Data-vector Blinding
### Likelihood Requirements
The blinding module requires the Firecrown likelihoods to be built with certain requirements. First we bust be able to build the likelihoods providing a [sacc](https://github.com/LSSTDESC/sacc/tree/master) object with the measurements for the data-vector:
```python
def build_likelihood(build_parameters):
    """
    This is a generic 3x2pt theory model, but with only
    bias as a systematic.

    """
    sacc_data = build_parameters['sacc_data']
```
(This is simular to what is currently done in [TXPipe](https://github.com/LSSTDESC/TXPipe/blob/df0dcc8c1e974576dd1942624ab5ff7bd0fbbaa0/txpipe/utils/theory_model.py#L19)).

The likelihood module also must have a method `.compute_theory_vector(ModellingTools)` which calls for the calculation of the theory vector inside the likelihood object. 

The likelihood can be provided either as a path to the python file containing the `build_likelihood` function or as a python module. In the latter case, the module must be imported.

## Legacy Blinding
Legacy Blinding scripts for 2pt data vector blinding with Cosmosis moved to a [new repository](https://github.com/LSSTDESC/legacy_blinding).

The [Legacy Blinding](https://github.com/LSSTDESC/legacy_blinding) repositories contains an updated version of Jessie Muir's scripts for blinding data-vectors using Cosmosis. The scripts have been adapted to work as a standalone module with Cosmosis V2 and [SACC](https://sacc.readthedocs.io/en/latest/) [Under Construction!].

> Under development. For questions contact @arthurmloureiro, @jessmuir, or @jablazek
