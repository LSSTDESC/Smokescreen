"""Define the likelihood factory function for the cosmic shear example.
Based on the firecrown example at
https://github.com/LSSTDESC/firecrown/blob/master/examples/cosmicshear/cosmicshear.py
and in the example likelihood at TXPipe:
https://github.com/LSSTDESC/TXPipe/blob/df0dcc8c1e974576dd1942624ab5ff7bd0fbbaa0/txpipe/utils/theory_model.py#L19
"""
import os
import sacc
import pathlib

import firecrown.likelihood.gauss_family.statistic.source.weak_lensing as wl
from firecrown.likelihood.gauss_family.statistic.two_point import TwoPoint
from firecrown.likelihood.gauss_family.gaussian import ConstGaussian
from firecrown.modeling_tools import ModelingTools

def build_likelihood(build_parameters):
    """
    Create a firecrown likelihood for a cosmic shear analysis.
    
    Parameters
    ----------
    build_parameters : dict
        Dictionary of parameters to be used in the likelihood.

    Returns
    -------
    likelihood : firecrown.likelihood.likelihood.Likelihood
        A firecrown likelihood object.
    """

    sacc_data = build_parameters['sacc_data']

    # items in the build_parameters are supposed to be
    # just str, int, etc, not complicated parameters.
    # this would abuse that slightly. We could always
    # write a temporary file to disc if needed.
    if isinstance(sacc_data, (str, pathlib.Path)):
        sacc_data = sacc.Sacc.load_fits(sacc_data)
    else:
        sacc_data = sacc_data.copy()
    # Creating sources, each one maps to a specific section of a SACC file. In
    # this case trc0, trc1 describe weak-lensing probes. The sources are saved
    # in a dictionary since they will be used by one or more two-point
    # functions.

    # We include a photo-z shift bias (a constant shift in dndz). We also
    # have a different parameter for each bin, so here again we use the
    # src{i}_ prefix.
    source0 = wl.WeakLensing(
        sacc_tracer="trc0", systematics=[wl.PhotoZShift(sacc_tracer="trc0")]
    )
    source1 = wl.WeakLensing(
        sacc_tracer="trc1", systematics=[wl.PhotoZShift(sacc_tracer="trc1")]
    )

    # Now that we have all sources we can instantiate all the two-point
    # functions. For each one we create a new two-point function object.

    # Creating all auto/cross-correlations two-point function objects for
    # the weak-lensing probes.
    stats = [
        TwoPoint("galaxy_shear_cl_ee", source0, source0),
        TwoPoint("galaxy_shear_cl_ee", source0, source1),
        TwoPoint("galaxy_shear_cl_ee", source1, source1),
    ]

    # Here we instantiate the actual likelihood. The statistics argument carry
    # the order of the data/theory vector.
    likelihood = ConstGaussian(statistics=stats)

    # two-point functions will receive the appropriated sections of the SACC
    # file and the sources their respective dndz.
    likelihood.read(sacc_data)

    modeling_tools = ModelingTools()

    # This script will be loaded by the appropriate connector. The framework
    # will call the factory function that should return a Likelihood instance.
    return likelihood, modeling_tools