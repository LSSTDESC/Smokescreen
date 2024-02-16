import pytest
from blinding.utils import string_to_seed

def test_string_to_seed():
    seed_string = "test_seed"
    result = string_to_seed(seed_string)
    
    # Check that the result is an integer
    assert isinstance(result, int)
    
    # Check that the same string produces the same seed
    assert string_to_seed(seed_string) == result

    # Check that a different string produces a different seed
    assert string_to_seed("different_seed") != result