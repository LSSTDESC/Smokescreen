import pytest
import sys
import os

from ..param_shifts import draw_param_shift
from ..param_shifts import DEFAULT_PARAM_RANGE

@pytest.fixture
def ranges():
    return {
        'param1': (0, 1),
        'param2': (-1, 1),
        'param3': (10, 20)
    }

def test_parameter_shifts(ranges):
    pdict = draw_param_shift(ranges=ranges)
    assert isinstance(pdict, dict)
    assert len(pdict) == len(ranges) + 1  # +1 for 'SHIFTS' key
    assert not pdict['SHIFTS']

    for param, value in pdict.items():
        if param != 'SHIFTS':
            assert value >= ranges[param][0]
            assert value <= ranges[param][1]

def test_parameter_shifts_with_default_range():
    pdict = draw_param_shift()
    assert isinstance(pdict, dict)
    assert len(pdict) == len(DEFAULT_PARAM_RANGE) + 1  # +1 for 'SHIFTS' key
    assert not pdict['SHIFTS']

    for param, value in pdict.items():
        if param != 'SHIFTS':
            assert value >= DEFAULT_PARAM_RANGE[param][0]
            assert value <= DEFAULT_PARAM_RANGE[param][1]

# def test_imported_parameter_shifts():
#     importfrom = 'other_module'
#     pdict = draw_param_shift(importfrom=importfrom)
#     assert isinstance(pdict, dict)
#     assert 'SHIFTS' in pdict

