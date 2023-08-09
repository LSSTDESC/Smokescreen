import logging
from .param_shifts import draw_flat_param_shift
from .io import get_parser
from .twopt_utils import get_dictkey_for_2pttype


def main():
    """
    main function to be called from command line
    """
    parser = get_parser()
    args = parser.parse_args()
    # Configure the logger level based on the input argument
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    # Create a logger for the __main__ module
    logger = logging.getLogger("2pt_blinding")
    logger.debug(args)

    params_shifts = draw_flat_param_shift(args.seed, args.paramshifts)
    logger.debug(params_shifts)

    

if __name__ == '__main__':
    main()
