import pytest  # noqa  F401
import pyccl as ccl
from smokescreen.param_shifts import draw_flat_param_shifts
from smokescreen.param_shifts import draw_flat_or_deterministic_param_shifts
from smokescreen.param_shifts import draw_gaussian_param_shifts


# tests for draw_flat_param_shifts
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


# tests for draw_flat_or_deterministic_param_shifts
def test_draw_flat_or_deterministic_param_shifts_deterministic():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": 0.01, "sigma8": 0.02}
    seed = 1234

    shifts = draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed)

    assert shifts["Omega_c"] == 0.01
    assert shifts["sigma8"] == 0.02


def test_draw_flat_or_deterministic_param_shifts_flat():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.01, 0.02), "sigma8": (0.02, 0.03)}
    seed = 1234

    shifts = draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed)

    assert 0.01 <= shifts["Omega_c"] <= 0.02
    assert 0.02 <= shifts["sigma8"] <= 0.03


def test_draw_flat_or_deterministic_param_shifts_invalid_key():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"invalid_param": 0.01}
    seed = 1234

    with pytest.raises(ValueError, match=r"Key invalid_param not in cosmology parameters"):
        draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed)


def test_draw_flat_or_deterministic_param_shifts_invalid_tuple_length():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.01, 0.02, 0.03)}
    seed = 1234

    with pytest.raises(ValueError, match=r"Tuple \(0.01, 0.02, 0.03\) has to be of length 2"):
        draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed)


def test_draw_flat_or_deterministic_param_shifts_string_seed():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.01, 0.02), "sigma8": (0.02, 0.03)}
    seed = "1234"

    shifts = draw_flat_or_deterministic_param_shifts(cosmo, shifts_dict, seed)

    assert 0.01 <= shifts["Omega_c"] <= 0.02
    assert 0.02 <= shifts["sigma8"] <= 0.03


# tests for draw_gaussian_param_shifts
def test_draw_gaussian_param_shifts_single_value():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.3, 0.01), "sigma8": (0.8, 0.02)}
    seed = 1234

    shifts = draw_gaussian_param_shifts(cosmo, shifts_dict, seed)

    assert isinstance(shifts, dict)
    assert set(shifts.keys()) == set(shifts_dict.keys())
    for key, value in shifts.items():
        mean, std = shifts_dict[key]
        assert mean - 3 * std <= value <= mean + 3 * std


def test_draw_gaussian_param_shifts_invalid_key():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"invalid_param": (0.3, 0.01)}
    seed = 1234

    with pytest.raises(ValueError, match=r"Key invalid_param not in cosmology parameters"):
        draw_gaussian_param_shifts(cosmo, shifts_dict, seed)


def test_draw_gaussian_param_shifts_invalid_tuple_length():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.3, 0.01, 0.02)}
    seed = 1234

    with pytest.raises(ValueError, match=r"Tuple \(0.3, 0.01, 0.02\) has to be of length 2"):
        draw_gaussian_param_shifts(cosmo, shifts_dict, seed)


def test_draw_gaussian_param_shifts_non_tuple_value():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": 0.3}
    seed = 1234

    with pytest.raises(ValueError, match=r"Value 0.3 has to be a tuple of length 2"):
        draw_gaussian_param_shifts(cosmo, shifts_dict, seed)


def test_draw_gaussian_param_shifts_string_seed():
    cosmo = ccl.CosmologyVanillaLCDM()
    shifts_dict = {"Omega_c": (0.3, 0.01), "sigma8": (0.8, 0.02)}
    seed = "1234"

    shifts = draw_gaussian_param_shifts(cosmo, shifts_dict, seed)

    assert isinstance(shifts, dict)
    assert set(shifts.keys()) == set(shifts_dict.keys())
    for key, value in shifts.items():
        mean, std = shifts_dict[key]
        assert mean - 3 * std <= value <= mean + 3 * std
