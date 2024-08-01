import pytest  # noqa  F401
from smokescreen.param_shifts import draw_flat_param_shifts


def test_single_value_shifts():
    shift_dict = {'param1': 1, 'param2': 2}
    seed = 123
    result = draw_flat_param_shifts(shift_dict, seed)
    assert isinstance(result, dict)
    assert set(result.keys()) == set(shift_dict.keys())
    for key, value in result.items():
        assert -shift_dict[key] <= value <= shift_dict[key]


def test_tuple_value_shifts():
    shift_dict = {'param1': (1, 2), 'param2': (2, 3)}
    seed = 123
    result = draw_flat_param_shifts(shift_dict, seed)
    assert isinstance(result, dict)
    assert set(result.keys()) == set(shift_dict.keys())
    for key, value in result.items():
        assert -shift_dict[key][0] <= value <= shift_dict[key][1]


def test_string_seed():
    shift_dict = {'param1': 1, 'param2': 2}
    seed = 'random_seed'
    result = draw_flat_param_shifts(shift_dict, seed)
    assert isinstance(result, dict)
    assert set(result.keys()) == set(shift_dict.keys())
    for key, value in result.items():
        assert -shift_dict[key] <= value <= shift_dict[key]
