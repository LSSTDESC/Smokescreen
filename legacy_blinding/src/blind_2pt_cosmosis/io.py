import argparse
from . import __version__

DEFAULT_PARAM_RANGE = {'cosmological_parameters--sigma_8_input':(0.834-3*.04,0.834+3*0.04),\
                       'cosmological_parameters--w':(-1.5,-.5)}

# DEFAULT_PARAM_RANGE = {'cosmological_parameters--sigma_8_input':(-3*0.04, 3*0.04),\
#                        'cosmological_parameters--w':(-0.5,0.5)}


class DictAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, eval(values))

def get_stored_seed_and_tag(args):
    """
    Obtains the seed and tag to be used in the output filename

    Parameters
    ----------
    args : argparse.Namespace
        Namespace with the arguments given by the user

    Returns
    -------
    storeseed : str
        Seed to be stored in the fits file
    tagstr : str
        Tag to be used in the output filename
    """
    if args.outftag is not None:
        tagstr = args.outftag # +'_'+tagstr
        if args.seedinfname:
            tagstr = tagstr + '_'+ args.seedstring
    elif args.seedinfname:
        tagstr = '_' + args.seedstring
    else:
        tagstr = ''

    if args.seedinfits:
        storeseed = args.seedstring
    else:
        storeseed = 'notsaved'
    return storeseed, tagstr

def get_parser():
    """
    creates the parser to obtain the user command line input
    """
    parser = argparse.ArgumentParser(
        prog='blind_2pt_cosmosis',
        formatter_class=argparse.RawTextHelpFormatter,
        description=f'''
    --------------------------------------------------------------------------------
    Blinding Module for 2pt data in Cosmosis. 
    Version {__version__}

    This is an adaptation of Jessie Muir's blind_2pt_usingcosmosis.py scripts.
    --------------------------------------------------------------------------------
    This module will apply a blinding factor to 2pt functios stored in a fits
    file, using cosmosis to compute the blinding factors.

    The workhorse function that puts everything together is do2ptblinding().
    This script can be called with command line arguments, or by calling that
    function in another script.

    The script uses cosmosis, so you'll need to  source its setup file before
    running this.

    ............................................................
    What it does:
    1. Using a string seed, pseudo-randomly draw a shift in parameters. This
    will eitherbe drawn from a flat distribution in some predefined parameter
    ranges, or from  a distribution defined in paramshiftmodule. Return
    dictionary of shifts where keys are parameter names matching those expected
    by run_cosmosis_togen_2ptdict.
    -> See draw_paramshift

    2. Using a cosmosis parameter ini file template, compute 2pt functions at
    reference and shifted cosmologies by running the cosmosis  twice. This
    should work no matter what sampler shows up in the template ini file.
    (If it uses the test sampler,  make sure the output is nothing, so that
    it doesn't save the cosmology and 2pt info.) Gets the 2pt functions into
    dictionaries of a specific format.
    -> See run_cosmosis_togen_2ptdict

    4. Take ratio or difference of 2pt datavectors to get blinding factor, in same
    dictionary format. (NOTE, MULTIPLICATIVE BLINDING IS CURRENTLY DISABLED)
    -> See get_factordict

    5. Apply blinding factor to desired datafile, saving a new fits file with
    string key in filename.
    -> See apply2ptblinding_tofits
    ............................................................
    Script maintained by Jessica Muir (jlmuir@stanford.edu).
    Module maintained by Arthur Loureiro (arthur.loureiro@fysik.su.se)
    --------------------------------------------------------------------------------
    ''', fromfile_prefix_chars='@')


    parser.add_argument("-u", "--origfits", type=str, required=True,
                        help='Name of unblinded fits file')

    parser.add_argument("-i", "--ini", type=str, required=False,
                        default='./src/blind_2pt_cosmosis/cosmosis_files/default_blinding_template.ini',
                        help='Ini file containing template for generating 2pt functions. \nShould'+
                        'use a binning that matches that of the origfits file' +
                        '\nReference a values file centered at desired reference' +
                        '\ncosmology')

    parser.add_argument('-s', '--seed', type=str, required=False, 
                        default="HARD_CODED_BLINDING",
                        help='string used to seed parameter shift selection')

    parser.add_argument('-t', '--bftype', type=str, required=False,
                        default='add',
                        help="Blinding factor type. Can be 'add', 'mult', or" + 
                        "'multNOCS' (mult with no cov scaling) \n[MULT OPTION IS DISABLED]. \n>> Default is 'add'")

    parser.add_argument('-o', '--outfname', type=str, required=False,
                        default=None,
                        help="Output filename; only set for testing,  " +
                        "If outftag is set, then " +
                        "\noutfname = [origfits]_[outftag]_[seed].fits." + 
                        "\n>> Default behavior is outfname = [origfits]_[seed].fits.")

    parser.add_argument('-f', '--outftag', type=str, required=False,
                        default="_BLINDED",
                        help="String to label output filename, for testing purposes. \nIf set" +
                        "when outfname is None (default), \nthen " +
                        "outfname = [origfits]_[outftag]_[seed].fits")
    
    parser.add_argument('-p', '--paramshifts', action=DictAction, required=False,
                        default=DEFAULT_PARAM_RANGE,
                        help="Dictionary of parameter shifts between quotes \". \nPlease use the parameter names" +
                        "as named in Cosmosis. \n>> Default is \"{'cosmological_parameters--sigma8_input':(0.834-3*.04,0.834"+
                        "+3*0.04),\ncosmological_parameters--w':(-1.5,-.5)}\"")
    
    parser.add_argument('--seedinfname', action='store_true', required=False,
                        default=False,
                        help="If set, appends seed to blinded data filename. Default is False.")
    
    parser.add_argument('--seedinfits', action='store_true', required=False,
                        default=False,
                        help="If set, stores seed in KEYWORD entry in blinded fits file. Default True.")
    
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Specify the logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL. Default is INFO.")
    return parser
