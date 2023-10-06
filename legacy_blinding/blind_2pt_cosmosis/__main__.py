import logging
from .param_shifts import draw_flat_param_shift
from .io import get_parser
from .run_cosmosis_2pt import run_cosmosis_togen_2ptdict


def main():
    """
    main function to be called from command line
    """
    # gets the parser from the io module
    parser = get_parser()
    args = parser.parse_args()

    # Configure the logger level based on the input argument
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a logger for the __main__ module
    logger = logging.getLogger("2pt_blinding")
    logger.debug(args)

    params_shifts = draw_flat_param_shift(args.seed, args.paramshifts)
    logger.debug(f"Parameters shifts are: {params_shifts}")

    #get blinding factors
    reff_dict = run_cosmosis_togen_2ptdict(inifile=args.ini) #args.ini is a template
    logger.debug(f"Calculated Reference Dict")
    #FIXME: Add nz_file and angles_file to args
    shift_dict = run_cosmosis_togen_2ptdict(inifile=args.ini, pdict=params_shifts,
                                            nz_file=None, angles_file=None)

if __name__ == '__main__':
    main()
