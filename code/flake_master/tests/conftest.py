import pytest

from code.flake_master.common_types import Flake8Preset


@pytest.fixture
def config_parser_with_data():
    return {
        'info': {'name': 'any name', 'revision': 'any revision'},
        'flake8_plugins': {'plugin': '1', 'plugin2': '2', 'plugin3': '3'},
        'flake8_config': {'config': '1', 'config2': '2', 'config3': '3'},
    }


@pytest.fixture
def row_config_data():
    return ('[info]\nname = any name\nrevision = any revision\n\n'
            '[flake8_plugins]\nplugin = 1\nplugin2 = 2\nplugin3 = 3\n\n'
            '[flake8_config]\nconfig = 1\nconfig2 = 2\nconfig3 = 3\n\n')


@pytest.fixture
def flake8_preset_factory(config_parser_with_data):
    def flake8_preset(config_url=None, filepath=None):
        return Flake8Preset(
                name=config_parser_with_data['info']['name'],
                revision=config_parser_with_data['info']['revision'],
                config_url=config_url,
                filepath=filepath,
                flake8_config=list(config_parser_with_data['flake8_config'].items()),
                flake8_plugins=list(config_parser_with_data['flake8_plugins'].items()),
            )
    return flake8_preset
