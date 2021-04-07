import pytest

from filecode.flake_master.common_types import Flake8Preset


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


@pytest.fixture()
def flake8_preset_factory(config_parser_dict):
    def flake8_preset(config_url=None, filepath=None):
        return Flake8Preset(
            name=config_parser_dict['info']['name'],
            revision=config_parser_dict['info']['revision'],
            config_url=config_url,
            filepath=filepath,
            flake8_plugins=list(config_parser_dict['flake8_plugins'].items()),
            flake8_config=list(config_parser_dict['flake8_config'].items()),
        )
    return flake8_preset


@pytest.fixture()
def read_data():
    return ('[info]\nname = name_value\nrevision = revision_value\n\n'
            '[flake8_plugins]\nkey_1 = value_1\n'
            '[flake8_config]\nkey_2 = value_2\n')
