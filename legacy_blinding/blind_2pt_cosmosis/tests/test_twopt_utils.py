import pytest
from ..twopt_utils import get_dictkey_for_2pttype

# FIXME: MISSING TESTS FOR spectrum_array_from_block

def test_get_dictkey_for_2pttype():

    type1 = 'GPR'
    type2 = 'G+R'
    xkey, ykey = get_dictkey_for_2pttype(type1, type2)

    assert xkey == 'galaxy_shear_xi_theta'
    assert ykey == 'galaxy_shear_xi'

    type1 = 'G+R'
    type2 = 'CKR'
    xkey, ykey = get_dictkey_for_2pttype(type1, type2)

    assert xkey == 'shear_cmbkappa_xi_theta'
    assert ykey == 'shear_cmbkappa_xi'

    type1 = 'CPR'
    type2 = 'GEF'

    with pytest.raises(ValueError):
        get_dictkey_for_2pttype(type1, type2)
