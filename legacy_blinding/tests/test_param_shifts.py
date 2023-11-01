import pytest
import numpy as np

from blind_2pt_cosmosis.param_shifts import draw_flat_param_shift
from blind_2pt_cosmosis.param_shifts import DEFAULT_PARAM_RANGE
from blind_2pt_cosmosis.param_shifts import apply_parameter_shifts

@pytest.fixture
def ranges():
    return {
        'param1': (0, 1),
        'param2': (-1, 1),
        'param3': (10, 20)
    }

def test_parameter_shifts(ranges):
    pdict = draw_flat_param_shift(ranges=ranges)
    assert isinstance(pdict, dict)
    assert len(pdict) == len(ranges) + 1  # +1 for 'SHIFTS' key
    assert not pdict['SHIFTS']

    for param, value in pdict.items():
        if param != 'SHIFTS':
            assert value >= ranges[param][0]
            assert value <= ranges[param][1]

def test_parameter_shifts_with_default_range():
    pdict = draw_flat_param_shift()
    assert isinstance(pdict, dict)
    assert len(pdict) == len(DEFAULT_PARAM_RANGE) + 1  # +1 for 'SHIFTS' key
    assert not pdict['SHIFTS']

    for param, value in pdict.items():
        if param != 'SHIFTS':
            assert value >= DEFAULT_PARAM_RANGE[param][0]
            assert value <= DEFAULT_PARAM_RANGE[param][1]

def test_draw_flat_param_shift():
    # Set a known seed to make the random draw predictable
    seedstring = 'test_seed'
    np.random.seed(42)  # Seed for np.random.rand

    # Test case 1: Using default parameter ranges
    pdict = draw_flat_param_shift(seedstring)
    assert 'SHIFTS' in pdict
    assert pdict['SHIFTS'] is False
    for param, (min_val, max_val) in DEFAULT_PARAM_RANGE.items():
        assert param in pdict
        assert min_val <= pdict[param] <= max_val

    # Test case 2: Custom parameter ranges
    custom_ranges = {'param1': (0.0, 1.0), 'param2': (-1.0, 1.0)}
    pdict = draw_flat_param_shift(seedstring, custom_ranges)
    assert 'SHIFTS' in pdict
    assert pdict['SHIFTS'] is False
    for param, (min_val, max_val) in custom_ranges.items():
        assert param in pdict
        assert min_val <= pdict[param] <= max_val

    # Test case 3: Check that a different seed produces different results
    pdict_1 = draw_flat_param_shift(seedstring)
    pdict_2 = draw_flat_param_shift('different_seed')
    assert pdict_1 != pdict_2

    # Test case 4: Check that providing the same seed produces the same result
    pdict_1 = draw_flat_param_shift(seedstring)
    pdict_2 = draw_flat_param_shift(seedstring)
    assert pdict_1 == pdict_2

# def test_apply_parameter_shifts():
#     # Create a mock pipeline with parameters
#     class MockParameter:
#         def __init__(self, name, start):
#             self.name = name
#             self.start = start

#     class MockPipeline:
#         def __init__(self, parameters):
#             self.parameters = parameters.name

#     # Define test parameters and expected results
#     parameters = [MockParameter('param1', 1.0), MockParameter('param2', 2.0)]
#     pdict = {'param1': 0.5, 'param2': 0.0, 'SHIFTS': True}
#     expected_start_values = {'param1': 1.5, 'param2': 2.0}

#     # Apply parameter shifts
#     pipeline = MockPipeline(parameters)
#     modified_pipeline = apply_parameter_shifts(pipeline, pdict)

#     # Check that the parameter values were shifted as expected
#     for parameter in modified_pipeline.parameters:
#         assert parameter.name in expected_start_values
#         assert parameter.start == expected_start_values[parameter.name]

#     # Ensure that the 'SHIFTS' parameter is removed from the dictionary
#     assert 'SHIFTS' not in pdict
