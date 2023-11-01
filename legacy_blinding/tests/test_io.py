import pytest
import argparse

from blind_2pt_cosmosis.io import get_parser, DictAction, get_stored_seed_and_tag

def test_dict_action():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action=DictAction)
    args = parser.parse_args(['--test', "{'key': 'value'}"])
    assert args.test == {'key': 'value'}

def test_get_parser():
    parser = get_parser()
    assert isinstance(parser, argparse.ArgumentParser)

def test_get_stored_seed_and_tag():
    # Test case 1: Default values
    args = argparse.Namespace(outftag=None, seedinfname=False, seedinfits=False, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'notsaved'
    assert tagstr == ''

    # Test case 2: outftag provided
    args = argparse.Namespace(outftag='output', seedinfname=False, seedinfits=False, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'notsaved'
    assert tagstr == 'output'

    # Test case 3: seedinfname and outftag provided
    args = argparse.Namespace(outftag='output', seedinfname=True, seedinfits=False, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'notsaved'
    assert tagstr == 'output_myseed'

    # Test case 4: seedinfits provided
    args = argparse.Namespace(outftag=None, seedinfname=False, seedinfits=True, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'myseed'
    assert tagstr == ''

    # Test case 5: seedinfname and seedinfits provided
    args = argparse.Namespace(outftag=None, seedinfname=True, seedinfits=True, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'myseed'
    assert tagstr == '_myseed'

    # Test case 6: All options provided
    args = argparse.Namespace(outftag='output', seedinfname=True, seedinfits=True, seedstring='myseed')
    storeseed, tagstr = get_stored_seed_and_tag(args)
    assert storeseed == 'myseed'
    assert tagstr == 'output_myseed'