import pathlib
from firecrown.data_functions import (
    extract_all_harmonic_data,
    check_two_point_consistence_harmonic,
)
from firecrown.likelihood.factories import load_sacc_data
from firecrown.likelihood import TwoPoint, TwoPointFactory
from firecrown.modeling_tools import ModelingTools, CCLCreationMode, CCLPureModeTransferFunction
from firecrown.modeling_tools import CCLFactory, PoweSpecAmplitudeParameter
from pyccl.neutrinos import NeutrinoMassSplits
from firecrown.metadata_types import TwoPointCorrelationSpace

import firecrown.likelihood.weak_lensing as wl
import firecrown.likelihood.number_counts as nc
from firecrown.likelihood.weak_lensing import PhotoZShiftFactory

from firecrown.likelihood import (
    ConstGaussian,
    Likelihood,
    NamedParameters,
)


def build_likelihood(
        build_parameters: NamedParameters,
) -> tuple[Likelihood, ModelingTools]:
    """
    Docstring for build_likelihood

    :param build_parameters: you should pass the following
        build_parameters:
        - sacc_data: path to a sacc file
        - factory_yaml: a yaml file with the firecrown systematics.
    """

    # load sacc data from build parameters
    try:
        sacc_data = build_parameters['sacc_data']
    except TypeError:
        sacc_data = build_parameters.data['sacc_data']

    # This is a trick TXPipe uses to pass a sacc file or object
    # to the likelihood. We need to check if the input is a string
    if isinstance(sacc_data, (str, pathlib.Path)):
        sacc_data = load_sacc_data(sacc_data)
    else:
        sacc_data = sacc_data.copy()

    # extract the relevant metadata and check things:
    two_point_cls = extract_all_harmonic_data(sacc_data)
    check_two_point_consistence_harmonic(two_point_cls)

    # WeakLensing systematics
    ia_systematic = wl.LinearAlignmentSystematicFactory()
    wl_photoz = PhotoZShiftFactory()
    wl_mult_bias = wl.MultiplicativeShearBiasFactory()

    wlf = wl.WeakLensingFactory(
        per_bin_systematics=[wl_mult_bias, wl_photoz],
        global_systematics=[ia_systematic],
    )

    # NumberCounts systematics
    nc_photoz = PhotoZShiftFactory()
    ncf = nc.NumberCountsFactory(
        per_bin_systematics=[nc_photoz],
        global_systematics=[],
    )

    all_two_point_functions = TwoPoint.from_measurement(
        two_point_cls,
        tp_factory=TwoPointFactory(
            correlation_space=TwoPointCorrelationSpace.HARMONIC,
            weak_lensing_factories=[wlf],
            number_counts_factories=[ncf],
        ),
    )

    likelihood_ready = ConstGaussian.create_ready(all_two_point_functions,
                                                  sacc_data.covariance.dense)

    tools = ModelingTools(ccl_factory=CCLFactory(
        require_nonlinear_pk=True,
        amplitude_parameter=PoweSpecAmplitudeParameter.AS,
        num_neutrino_masses=None,
        mass_split=NeutrinoMassSplits.EQUAL,
        creation_mode=CCLCreationMode.DEFAULT,
        pure_ccl_transfer_function=CCLPureModeTransferFunction.BOLTZMANN_CAMB,
        use_camb_hm_sampling=False,
        allow_multiple_camb_instances=False,
        camb_extra_params=None,
        )
        )

    return likelihood_ready, tools
