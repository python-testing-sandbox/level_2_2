import json
from unittest.mock import Mock, mock_open

import pytest
from click.testing import CliRunner

from code.flake_master.run import setup_preset, upgrade_preset


@pytest.mark.parametrize(
    'is_path_exists, preset',
    [
        (True, None),
        (False, None),
        (False, Mock(name='preset_name', revision='revision'))
    ]
)
def test_setup_preset(mocker, is_path_exists, preset):
    runner = CliRunner()
    obj = {'preset_file_name': '.flake_master'}
    preset_name = 'name'
    project_path = 'path'
    file_path = 'file_path'

    mocker.patch('code.flake_master.run.Path.convert', Mock(return_value=project_path))
    mocker.patch('code.flake_master.run.os.path.exists', Mock(return_value=is_path_exists))
    mocker.patch('code.flake_master.run.os.path.join', Mock(return_value=file_path))
    mocker.patch('code.flake_master.run.fetch_preset', Mock(return_value=preset))
    mocker.patch('code.flake_master.run.apply_preset_to_path')

    if is_path_exists:
        expected_output = (f'Preset file ({file_path}) already exists. Looks like flake master '
                           f'has already been deployed to {project_path}. May be you mean `upgrade`, not `setup`?\n')
        expected_exit_code = 1
    elif not is_path_exists and not preset:
        expected_output = f'Error fetching preset {preset_name}.\n'
        expected_exit_code = 1
    else:
        expected_output = f'Fetched {preset.name} v. {preset.revision}\nPreset {preset.name} applied.\n'
        expected_exit_code = 0

    result = runner.invoke(setup_preset, [preset_name, project_path], obj=obj)

    assert result.output == expected_output
    assert result.exit_code == expected_exit_code


@pytest.mark.parametrize(
    'is_path_exists, preset_info_row',
    [
        (False, '{}'),
        (True, '{"name": "preset_name", "revision": "1"}'),
        (True, '{"name": "preset_name", "revision": "3"}'),
    ]
)
def test_upgrade_preset(mocker, is_path_exists, preset_info_row):
    runner = CliRunner()
    obj = {'preset_file_name': '.flake_master'}
    project_path = 'path'
    file_path = 'file_path'
    fresh_preset_revision = '2'
    preset_info = json.loads(preset_info_row)

    mocker.patch('code.flake_master.run.Path.convert', Mock(return_value=project_path))
    mocker.patch('code.flake_master.run.os.path.exists', Mock(return_value=is_path_exists))
    mocker.patch('code.flake_master.run.os.path.join', Mock(return_value=file_path))
    fetch_preset = mocker.patch('code.flake_master.run.fetch_preset')
    fresh_preset = fetch_preset()
    fresh_preset.revision = fresh_preset_revision
    mocker.patch('code.flake_master.run.apply_preset_to_path')
    mocker.patch('code.flake_master.run.open', mock_open(read_data=preset_info_row))

    if not is_path_exists:
        expected_output = (f'Preset file ({file_path}) not found. Looks like flake master '
                           f'was not deployed to {project_path}. May be you mean `setup`, not `upgrade`?\n')
        expected_exit_code = 1
    elif is_path_exists and fresh_preset.revision > preset_info['revision']:
        expected_output = (f'Updating preset {preset_info["name"]} from rev. '
                           f'{preset_info["revision"]} to {fresh_preset.revision}...\n')
        expected_exit_code = 0
    else:
        expected_output = ''
        expected_exit_code = 0

    result = runner.invoke(upgrade_preset, [project_path], obj=obj)

    assert result.output == expected_output
    assert result.exit_code == expected_exit_code
