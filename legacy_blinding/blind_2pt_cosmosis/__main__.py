from .param_shifts import draw_flat_param_shift
from .io import get_parser

def main():
    """
    main function to be called from command line
    """
    parser = get_parser()
    args = parser.parse_args()
    print(args)

    params_shifts = draw_flat_param_shift(args.seed, args.paramshifts)
    print(params_shifts)
    # print the keys inside the dictionary
    print(params_shifts.keys())

if __name__ == '__main__':
    main()
