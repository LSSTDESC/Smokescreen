import time
import logging
from cosmosis.runtime.config import Inifile
from cosmosis.runtime.pipeline import LikelihoodPipeline
from .twopt_utils import get_twoptdict_from_pipeline_data
from .param_shifts import apply_parameter_shifts

logger = logging.getLogger("2pt_blinding")

def setup_pipeline(inifile, angles_file=None, nz_file=None):
    """
    Initialize and set up the Cosmosis pipeline.
    """
    ini = Inifile(inifile)
    # Modify settings to suppress unnecessary outputs
    ini = modify_settings(ini, angles_file, nz_file)
    pipeline = LikelihoodPipeline(ini)
    return pipeline

def modify_settings(ini, angles_file=None, nz_file=None):
    """
    Modify pipeline settings to suppress unnecessary outputs.
    """
    sections_to_modify = ['test', 'output']
    for section in sections_to_modify:
        if section in ini.__dict__['_sections']:
            ini.__dict__['_sections'][section]['save_dir'] = ''
    ini.__dict__['_sections']['pipeline']['debug'] = 'F'
    ini.__dict__['_sections']['pipeline']['quiet'] = 'T'

    # a structure like what follows could be used to make sure
    # angles and n(z) are being used consistently with file being blinded
    # as in, make sure that they are referencing it for angles and n(z).
    # However, this isn't really ideal, as how it is set up will be specific
    #   to the 3x2pt pipeline and may cause issues when/if the same script
    #   is bein used for 5x2pt or other observables. Really the template ini
    #   file should handle these choices, and hsould be set up in the same way
    #   that you would set up an ini file to do parameter estimation on your
    #   data file. 
    if angles_file is not None:  #fits file to get theta ranges from
        hadsections=[]
        for section in ['shear_2pt_eplusb','shear_2pt_eminusb','2pt_gal','2pt_gal_shear']:
            if section in ini.__dict__['_sections'].keys():
                ini.__dict__['_sections'][section]['theta_file']=angles_file
                hadsections.append(section)
        print("CHANGED theta_file TO ",angles_file," FOR:",hadsections," \n IF YOU MEANT TO CHANGE IT FOR OTHER 2PT FUNCTIONS, SOMETHING WENT WRONG.")
                
    if nz_file is not None:   # fits file to get n(z) from
        section = 'fits_nz'
        if section in ini.__dict__['_sections'].keys():
            ini.__dict__['_sections'][section]['nz_file']=nz_file
        else:
            raise ValueError("You specified nz_file as "+nz_file+", but I can't find the fits_nz module settings in  your ini file.")
    return ini

def run_pipeline(pipeline):
    """
    Run the Cosmosis pipeline and return the data.
    """
    data = pipeline.run_parameters([])
    return data

def run_cosmosis_togen_2ptdict(inifile, pdict={},
                                nz_file=None, angles_file=None):
    """
    Runs cosmosis pipeline to generate 2pt functions.
    """
    logger.debug("Running cosmosis pipeline to generate 2pt functions.")
    pipeline = setup_pipeline(inifile, angles_file, nz_file)
    logger.debug("Passed setup_pipeline.")
    # need to set all of the parameters to be fixed for run_parameters([])
    #  to work. Doing this will effectively run things like the test sampler
    #  no matter what sampler is listed in the ini file
    for parameter in pipeline.parameters:
        pipeline.set_fixed(parameter.section, parameter.name, parameter.start)
    # if we need to do shifts:
    if len(list(pdict.keys())) > 0:
        logger.debug("Applying parameter shifts.")
        pipeline = apply_parameter_shifts(pipeline, pdict)
    else:
        logger.debug("No parameter shifts to apply.")

    data = run_pipeline(pipeline)
    logger.debug("Passed run_pipeline.")
    
    twoptdict = get_twoptdict_from_pipeline_data(data)
    logger.debug(f"Passed get_twoptdict_from_pipeline_data!")
    
    return twoptdict
