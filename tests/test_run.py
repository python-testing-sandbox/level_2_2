import pytest
from click.testing import CliRunner

from filecode.flake_master.run import flake_setup, upgrade


@pytest.mark.parametrize(
    'exists, is_fetch, output, exit_code',
    [
        (True, False, 'Preset file (path) already exists. Looks like flake master has already '
                      'been deployed to path. May be you mean `upgrade`, not `setup`?\n', 1),
        (False, True, 'Fetched name v. revision\nPreset name applied.\n', 0),
        (False, False, 'Error fetching preset rose.\n', 1),
    ],
)
def test_flake_setup(mocker, exists, is_fetch, output, exit_code):
    obj = {'preset_file_name': '.flake_master'}
    mocker.patch('filecode.flake_master.run.Path.convert', mocker.Mock(return_value='path'))
    fetch_preset = mocker.patch('filecode.flake_master.run.fetch_preset', return_value=None)
    if is_fetch:
        fetch_preset.return_value = mocker.Mock()
        fetch_preset().name = 'name'
        fetch_preset().revision = 'revision'
    mocker.patch('filecode.flake_master.run.apply_preset_to_path')
    os = mocker.patch('filecode.flake_master.run.os', spec=['path'])
    os.path.join.return_value = 'path'
    os.path.exists.return_value = exists

    runner = CliRunner()
    result = runner.invoke(flake_setup, ['rose', 'path'], obj=obj)
    assert result.output == output
    assert result.exit_code == exit_code


@pytest.mark.parametrize(
    'exists, preset_info, output, exit_code',
    [
        (True, '{"revision": 0, "name": "name"}', 'Updating preset name from rev. 0 to 1...\n', 0),
        (True, '{"revision": 1}', '', 0),
        (False, '{}', 'Preset file (path) not found. Looks like flake master was not '
                      'deployed to path. May be you mean `setup`, not `upgrade`?\n', 1),
    ],
)
def test_upgrade(mocker, exists, preset_info, output, exit_code):
    obj = {'preset_file_name': '.flake_master'}
    mocker.patch('filecode.flake_master.run.Path.convert', mocker.Mock(return_value='path'))
    os = mocker.patch('filecode.flake_master.run.os', spec=['path'])
    os.path.join.return_value = 'path'
    os.path.exists.return_value = exists
    mocker.patch('filecode.flake_master.run.open', mocker.mock_open(read_data=preset_info))
    fetch_preset = mocker.patch('filecode.flake_master.run.fetch_preset', return_value=mocker.Mock())
    fetch_preset().revision = 1
    mocker.patch('filecode.flake_master.run.apply_preset_to_path')

    runner = CliRunner()
    result = runner.invoke(upgrade, ['path'], obj=obj)
    assert result.output == output
    assert result.exit_code == exit_code
