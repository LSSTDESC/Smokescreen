"""Define the likelihood factory function for the supernovae ia example.
Based on the firecrown example at
https://github.com/LSSTDESC/firecrown/blob/master/examples/srd_sn/sn_srd.py
"""
import sacc
import pathlib
from packaging.version import Version
import firecrown
if Version(firecrown.__version__) >= Version("1.8"):
    # future proofing for firecrown 1.8
    import firecrown.likelihood.supernova as sn
    from firecrown.likelihood.gaussian import ConstGaussian
else:
    from firecrown.likelihood.gauss_family.statistic import supernova as sn
    from firecrown.likelihood.gauss_family.gaussian import ConstGaussian
from firecrown.modeling_tools import ModelingTools
from firecrown.likelihood.likelihood import NamedParameters


def build_likelihood(build_parameters: NamedParameters):
    """
    Create a firecrown likelihood for a supernovae type Ia analysis.

    Parameters
    ----------
    build_parameters : NamedParameters
        Dictionary of parameters to be used in the likelihood.

    Returns
    -------
    likelihood : firecrown.likelihood.likelihood.Likelihood
        A firecrown likelihood object.
    """

    try:
        sacc_data = build_parameters['sacc_data']
    except TypeError:
        sacc_data = build_parameters.data['sacc_data']

    # This is a trick TXPipe uses to pass a sacc file or object
    # to the likelihood. We need to check if the input is a string
    if isinstance(sacc_data, (str, pathlib.Path)):
        sacc_data = sacc.Sacc.load_fits(sacc_data)
    else:
        sacc_data = sacc_data.copy()

    # instantiate the necessary objects to deal with SNe Ia data
    snia_stats = sn.Supernova(sacc_tracer="sn_ddf_sample")

    # Here we instantiate the actual likelihood. The statistics argument carry
    # the order of the data/theory vector.
    likelihood = ConstGaussian(statistics=[snia_stats])
    likelihood.read(sacc_data)

    modeling_tools = ModelingTools()

    # This script will be loaded by the appropriate connector. The framework
    # will call the factory function that should return a Likelihood instance.
    return likelihood, modeling_tools
