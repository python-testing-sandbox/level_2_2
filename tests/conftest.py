import pytest


@pytest.fixture()
def mock_parse_preset_from_str_config(mocker):
    return mocker.patch('filecode.flake_master.utils.preset_fetchers.parse_preset_from_str_config')


@pytest.fixture()
def config_parser_dict():
    return {
        'info': {'name': 'name_value', 'revision': 'revision_value'},
        'flake8_plugins': {'key_1': 'value_1'},
        'flake8_config': {'key_2': 'value_2'}
    }


@pytest.fixture()
def os(mocker):
    return mocker.patch('filecode.flake_master.utils.presets.os', spec=['path'])
