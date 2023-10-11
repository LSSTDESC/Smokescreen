import pytest
from blind_2pt_cosmosis.twopt_utils import get_dictkey_for_2pttype 
from blind_2pt_cosmosis.twopt_utils import get_twoptdict_from_pipeline_data
from blind_2pt_cosmosis.twopt_utils import spectrum_array_from_block

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


# # A mock datablock object for testing
# class MockDatablock:
#     def has_section(self, section):
#         return section in ['section1', 'section2']

# # A mock spectrum_array_from_block function for testing
# def mock_spectrum_array_from_block(data, section, types, xlabel, binformat):
#     return [1, 2, 3], [4, 5, 6], [0.5, 1.0, 1.5], True, [0.4, 0.9, 1.4], [0.6, 1.1, 1.6]

# def test_get_twoptdict_from_pipelinedata():
#     data = MockDatablock()
#     original_spectrum_array_from_block = your_module.spectrum_array_from_block
#     your_module.spectrum_array_from_block = mock_spectrum_array_from_block
    
#     result = get_twoptdict_from_pipelinedata(data)
    
#     your_module.spectrum_array_from_block = original_spectrum_array_from_block
    
#     assert 'galaxy_position_real_theta' in result
#     assert 'galaxy_position_real_xi' in result
#     assert 'galaxy_position_real_xi_bins' in result
#     assert 'galaxy_position_real_xi_binavg' in result
#     assert 'galaxy_position_real_theta_mins' in result
#     assert 'galaxy_position_real_theta_maxs' in result
    
#     assert 'cmb_kappa_real_ell' in result
#     assert 'cmb_kappa_real_cl' in result
#     assert 'cmb_kappa_real_cl_bins' in result
#     assert 'cmb_kappa_real_cl_binavg' in result
#     assert 'cmb_kappa_real_ell_mins' in result
#     assert 'cmb_kappa_real_ell_maxs' in result