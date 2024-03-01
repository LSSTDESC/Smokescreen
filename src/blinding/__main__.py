import numpy as np
from typing import Union
from jsonargparse import CLI
from jsonargparse.typing import Path_drw, Path_fr
from pyccl import Cosmology as CosmologyType
import pyccl as ccl

from blinding.smokescreen import Smokescreen

def main(path_to_sacc: Path_drw, likelihood_path: Path_fr, systematics: dict,
         shifts_dict: dict, seed: Union[int, str],
         cosmo: Union[CosmologyType, dict] = ccl.CosmologyVanillaLCDM()):
    """Main function to run the blinding process.

    Args:
        cosmo (dict): Dictionary with the reference cosmological parameters.
        systematics (dict): Dictionary with the reference firecrown likelihood systematic parameters.
        likelihood_path (str): Path to the firecrown likelihood module file.
    """
    print("inside main")
    print(path_to_sacc)
    print(cosmo._params_init_kwargs)

if __name__ == "__main__":
    CLI(main, as_positional=False)