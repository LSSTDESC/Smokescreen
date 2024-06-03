import numpy as np
from typing import Union
from jsonargparse import CLI
from jsonargparse.typing import Path_drw, Path_fr
from pyccl import Cosmology as CosmologyType
import pyccl as ccl

from blinding.smokescreen import Smokescreen

def main(path_to_sacc: Path_drw, likelihood_path: Path_fr, systematics: dict,
         shifts_dict: dict, seed: Union[int, str] = 2112,
         cosmo: Union[CosmologyType, dict] = ccl.CosmologyVanillaLCDM()):
    """Main function to conceal a sacc file using a firecrown likelihood TEST.

    FIXME: Add shift type!

    Args:
        path_to_sacc (str): Path to the sacc file to blind.
        likelihood_path (str): Path to the firecrown likelihood module file.
        systematics (dict): Dictionary with fixed values for the firecrown systematics parameters.
        shifts_dict (dict): Dictionary with fixed values for the firecrown shifts parameters. 
            Example: {"Omega_c": (0.20, 0.39), "sigma8": (0.70, 0.90)}
        seed (int, str): Seed for the blinding process. Defaults to 2112.
        cosmo (Union[CosmologyType, dict]): Cosmology object or dictionary with cosmological parameters.
            Defaults to ccl.CosmologyVanillaLCDM().
    """
    print("inside main")
    print(path_to_sacc)
    print(cosmo._params_init_kwargs)

if __name__ == "__main__":
    CLI(main, as_positional=False)