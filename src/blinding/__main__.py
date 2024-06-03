import os
import numpy as np
from typing import Union, Dict, Tuple
from jsonargparse import CLI
from jsonargparse.typing import Path_drw, Path_fr
from pyccl import Cosmology as CosmologyType
import pyccl as ccl
import sacc


from blinding.smokescreen import Smokescreen
from blinding.utils import load_cosmology_from_partial_dict


def main(path_to_sacc: Path_fr,
         likelihood_path: str,
         systematics: dict,
         shifts_dict: Dict[str, Tuple[float, float]],
         seed: Union[int, str] = 2112,
         cosmo: Union[CosmologyType, dict] = ccl.CosmologyVanillaLCDM()):
    """Main function to conceal a sacc file using a firecrown likelihood.

    FIXME: Add shift type!

    Args:
        path_to_sacc (str): Path to the sacc file to blind.
        likelihood_path (str): Path to the firecrown likelihood module file.
        systematics (dict): Dictionary with fixed values for the firecrown systematics parameters.
        shifts_dict (dict): Dictionary with fixed values for the firecrown shifts parameters. 
            Example: {"Omega_c": (0.20, 0.39), "sigma8": (0.70, 0.90)}
        seed (int, str): Seed for the blinding process. Defaults to 2112.
        cosmo (Union[CosmologyType, dict]): Cosmology object or dictionary with cosmological parameters you want different than the
        VanillaLCDM as reference cosmology.
            Defaults to ccl.CosmologyVanillaLCDM().
    """
    # tests if the sacc file exists
    assert os.path.exists(path_to_sacc), f"File {path_to_sacc} does not exist."
    assert os.path.exists(likelihood_path), f"File {likelihood_path} does not exist."
    # reads the sacc file
    sacc_data = sacc.Sacc.load_fits(path_to_sacc)
    print(type(likelihood_path))
    # creates the smokescreen object
    smoke = Smokescreen(cosmo, systematics, likelihood_path, shifts_dict, sacc_data, seed)
    # blinds the sacc file
    smoke.calculate_blinding_factor(factor_type='add')
    # applies the blinding factor to the sacc file
    smoke.apply_blinding_to_likelihood_datavec()
    # saves the blinded sacc file

if __name__ == "__main__":
    CLI(main, as_positional=False)