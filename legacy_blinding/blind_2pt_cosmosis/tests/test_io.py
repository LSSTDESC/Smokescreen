import pytest
import argparse

from ..io import get_parser, DictAction

def test_dict_action():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action=DictAction)
    args = parser.parse_args(['--test', "{'key': 'value'}"])
    assert args.test == {'key': 'value'}

def test_get_parser():
    parser = get_parser()
    assert isinstance(parser, argparse.ArgumentParser)

# def test_get_parser():
#     parser = get_parser()
#     assert isinstance(parser, argparse.ArgumentParser)

#     # Test argument presence
#     assert hasattr(parser, 'prog')
#     assert hasattr(parser, 'description')
#     assert hasattr(parser, 'add_argument')

#     # Test argument defaults
#     args = parser.parse_args([])
#     assert args.origfits is None
#     assert args.ini == 'default_blinding_template.ini'
#     assert args.seed == 'HARD_CODED_BLINDING'
#     assert args.bftype == 'add'
#     assert args.outfname is None
#     assert args.outftag == '_BLINDED'
#     assert args.paramshifts == {
#         'cosmological_parameters--sigma8_input': (0.834 - 3 * 0.04, 0.834 + 3 * 0.04),
#         'cosmological_parameters--w': (-1.5, -0.5)
#     }
#     assert not args.seedinfname
#     assert args.seedinfits

#     # Test argument help messages
#     assert parser.get_description().startswith('    --------------------------------------------------------------------------------')
#     assert parser.get_usage().startswith('usage: blind_2pt_cosmosis')

#     # Test argument types and choices
#     assert isinstance(parser.prog, str)
#     assert isinstance(parser.ini, argparse.FileType)
#     assert isinstance(parser.seed, str)
#     assert isinstance(parser.bftype, str)
#     assert isinstance(parser.outfname, str)
#     assert isinstance(parser.outftag, str)
#     assert isinstance(parser.paramshifts, DictAction)
#     assert isinstance(parser.seedinfname, bool)
#     assert isinstance(parser.seedinfits, bool)
