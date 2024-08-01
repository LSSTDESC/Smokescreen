import os
import getpass
from typing import Union, Dict, Tuple
from jsonargparse import CLI
from jsonargparse.typing import Path_drw, Path_fr
from pyccl import Cosmology as CosmologyType
import pyccl as ccl
import sacc
# warnings related to sacc files
import warnings
from smokescreen import ConcealDataVector
from smokescreen.utils import load_cosmology_from_partial_dict
from . import __version__
warnings.filterwarnings("ignore")

# banner to be printed in the terminal
banner = rf"""

 (                                                          
 )\ )                 )                                     
(()/(    )         ( /(    (          (      (    (         
 /(_))  (      (   )\())  ))\ (    (  )(    ))\  ))\  (     
(_))    )\  '  )\ ((_)\  /((_))\   )\(()\  /((_)/((_) )\ )  
/ __| _((_))  ((_)| |(_)(_)) ((_) ((_)((_)(_)) (_))  _(_/(  
\__ \| '  \()/ _ \| / / / -_)(_-</ _|| '_|/ -_)/ -_)| ' \)) 
|___/|_|_|_| \___/|_\_\ \___|/__/\__||_|  \___|\___||_||_|  
                                                            
     - DESC Pipeline for Concealing your data-vector -
                       Version {__version__}
"""


def main(path_to_sacc: Path_fr,
         likelihood_path: str,
         systematics: dict,
         shifts_dict: Dict[str, Tuple[float, float]],
         shift_type: str = 'add',
         seed: Union[int, str] = 2112,
         reference_cosmology: Union[CosmologyType, dict] = ccl.CosmologyVanillaLCDM(),
         path_to_output: Path_drw = None):
    """Main function to conceal a sacc file using a firecrown likelihood.

    Args:
        path_to_sacc (str): Path to the sacc file to blind.
        likelihood_path (str): Path to the firecrown likelihood module file.
        systematics (dict): Dictionary with fixed values for the firecrown systematics parameters.
        shifts_dict (dict): Dictionary with fixed values for the firecrown shifts parameters.
            Example: {"Omega_c": (0.20, 0.39), "sigma8": (0.70, 0.90)}
        shift_type (str): Type of shift to apply to the data vector. 
            Options are 'add' and 'mult'. Defaults to 'add'.
        seed (int, str): Seed for the blinding process. Defaults to 2112.
        reference_cosmology (Union[CosmologyType, dict]): 
            Cosmology object or dictionary with cosmological 
            parameters you want different than the VanillaLCDM as reference cosmology.
            Defaults to ccl.CosmologyVanillaLCDM().
        path_to_output (str): Path to save the blinded sacc file. Defaults to None.
    """
    print(banner)
    if isinstance(reference_cosmology, dict):
        cosmo = load_cosmology_from_partial_dict(reference_cosmology)
    else:
        cosmo = reference_cosmology
    # tests if the sacc file exists
    assert os.path.exists(path_to_sacc), f"File {path_to_sacc} does not exist."
    assert os.path.exists(likelihood_path), f"File {likelihood_path} does not exist."
    # reads the sacc file
    sacc_data = sacc.Sacc.load_fits(path_to_sacc)
    # creates the smokescreen object
    smoke = ConcealDataVector(cosmo, systematics, likelihood_path, shifts_dict, sacc_data, seed)
    # blinds the sacc file
    smoke.calculate_concealing_factor(factor_type=shift_type)
    # applies the blinding factor to the sacc file
    smoke.apply_concealing_to_likelihood_datavec()
    print(f">> User {getpass.getuser()}",
          "used Smokescreen on {path_to_sacc} ... it is super effective!")
    # get root name of the input file
    root_name = os.path.splitext(os.path.basename(path_to_sacc))[0]
    # saves the blinded sacc file
    if path_to_output is not None:
        smoke.save_concealed_datavector(path_to_output, root_name)
    else:
        # get the input file directory
        path_to_output = os.path.dirname(path_to_sacc)
        smoke.save_concealed_datavector(path_to_output, root_name)
    print(f"\nConcealed sacc file saved as {path_to_output}/{root_name}_concealed_data_vector.fits")


if __name__ == "__main__":  # pragma: no cover
    CLI(main, as_positional=False)
