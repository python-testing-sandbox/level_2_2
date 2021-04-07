import pytest

import filecode

from filecode.flake_master.utils.preset_fetchers import load_preset_from_file, load_preset_from_url, \
    parse_preset_from_str_config
from filecode.flake_master.utils.presets import (
    extract_preset_url, extract_preset_file_path, apply_preset_to_path,
    add_packages_to_requirements_file, add_flake8_config, create_preset_file, extract_preset_credentials)
from filecode.flake_master.utils.requirements import merge_requirements_data, find_requirement_in_list


def test_load_preset_from_file(mocker, flake8_preset_factory, read_data):
    mocker.patch('filecode.flake_master.utils.preset_fetchers.open', mocker.mock_open(read_data=read_data))
    expected = flake8_preset_factory(filepath='filepath')
    assert load_preset_from_file('filepath') == expected


def test_load_preset_from_url(mocker, flake8_preset_factory, read_data):
    get = mocker.patch('filecode.flake_master.utils.preset_fetchers.get')
    get().text = read_data
    expected = flake8_preset_factory(config_url='url')
    assert load_preset_from_url('url') == expected
    get.assert_called_with('url')


def test_parse_preset_from_str_config(mocker, flake8_preset_factory, config_parser_dict):
    parser = mocker.patch('filecode.flake_master.utils.preset_fetchers.configparser')
    parser.ConfigParser().__getitem__.side_effect = config_parser_dict.__getitem__
    expected = flake8_preset_factory(config_url='url', filepath='filepath')
    assert parse_preset_from_str_config('text', 'filepath', 'url') == expected


@pytest.mark.parametrize(
    'filepath, url, expected',
    [
        ('filepath', 'url', 'load_preset_from_file'),
        ('filepath', '', 'load_preset_from_file'),
        ('', 'url', 'load_preset_from_url'),
        ('', '', None),
    ]
)
def test_fetch_preset(mocker, filepath, url, expected):
    mocker.patch('filecode.flake_master.utils.presets.extract_preset_credentials', return_value=(filepath, url))
    mocker.patch('filecode.flake_master.utils.presets.load_preset_from_file', return_value='load_preset_from_file')
    mocker.patch('filecode.flake_master.utils.presets.load_preset_from_url', return_value='load_preset_from_url')
    assert filecode.flake_master.utils.presets.fetch_preset('name', 'info', 'url') == expected


def test_extract_preset_credentials(mocker):
    mocker.patch(
        'filecode.flake_master.utils.presets.extract_preset_file_path',
        return_value='extract_preset_file_path',
    )
    mocker.patch('filecode.flake_master.utils.presets.extract_preset_url', return_value='extract_preset_url')
    assert extract_preset_credentials('name', 'info', 'url') == ('extract_preset_file_path', 'extract_preset_url')


@pytest.mark.parametrize(
    'preset_name_or_url_or_path, preset_info, is_path_exists, expected',
    [
        ('name.cfg', {'filepath': 'path'}, True, 'path'),
        ('name.cfg', {'filepath': ''}, True, 'abspath'),
        ('name', {'filepath': ''}, True, None),
        ('', {'filepath': 'path'}, True, 'path'),
        ('', {}, False, None),
    ],
)
def test_extract_preset_file_path(os, preset_name_or_url_or_path, preset_info, is_path_exists, expected):
    os.path.exists.return_value = is_path_exists
    os.path.abspath.return_value = 'abspath'
    assert extract_preset_file_path(preset_name_or_url_or_path, preset_info) == expected


@pytest.mark.parametrize(
    'preset_name_or_url_or_path, preset_info, presets_repo_url, expected',
    [
        ('http://url', {'url': 'preset url'}, 'github', 'preset url'),
        ('url', {}, 'github', 'github/master/presets/url.cfg'),
        ('', {}, 'github', None),
        ('url', {'url': ''}, 'github', 'github/master/presets/url.cfg'),
    ],
)
def test_extract_preset_url(preset_name_or_url_or_path, preset_info, presets_repo_url, expected):
    assert extract_preset_url(preset_name_or_url_or_path, preset_info, presets_repo_url) == expected


def test_apply_preset_to_path(mocker, capsys):
    path = 'path'
    add_packages_to_requirements_file = mocker.patch(
        'filecode.flake_master.utils.presets.add_packages_to_requirements_file',
    )
    add_flake8_config = mocker.patch('filecode.flake_master.utils.presets.add_flake8_config')
    create_preset_file = mocker.patch('filecode.flake_master.utils.presets.create_preset_file')
    preset = mocker.Mock()
    preset.flake8_plugins = ['plugins']
    preset.flake8_config = 'config'

    apply_preset_to_path(preset, path, 'file_name')
    out, err = capsys.readouterr()

    assert out == '\tAdding 1 requirements...\n\tCreating flake8 config...\n\tCreating preset file...\n'
    add_packages_to_requirements_file.assert_called_with(
        preset.flake8_plugins,
        path,
        requirements_files_names=['requirements.txt', 'requirements.txt'],
        default_requirements_file_name='requirements.txt',
    )
    add_flake8_config.assert_called_with('config', path, config_file_name='setup.cfg')
    create_preset_file.assert_called_with(preset, path, preset_file_name='file_name')


@pytest.mark.parametrize(
    'is_path_exists',
    [
        (True),
        (False),
    ],
)
def test_add_packages_to_requirements_file(os, tmpdir, capsys, is_path_exists):
    raw_old_requirements = 'coverage==5.5\npytest==6.2.2\n'
    flake_plugins = [('flake', '3'), ('flake', '8')]

    file = tmpdir.join('example.txt')
    file.write(raw_old_requirements)
    os.path.join.return_value = file.strpath
    os.path.exists.return_value = is_path_exists
    add_packages_to_requirements_file(flake_plugins, 'path', ['filename'], 'default_filename')
    out, err = capsys.readouterr()

    if is_path_exists:
        assert out == f'\t\tadding to {file.strpath}...\n'
        assert file.read() == 'coverage==5.5\npytest==6.2.2\nflake==3\nflake==8\n'
    else:
        assert out == '\t\tcreating default_filename...\n'
        assert file.read() == 'flake==3\nflake==8'


@pytest.mark.parametrize(
    'is_path_exists, params',
    [
        (True, {'flake8': {'flake': 'param', 'key': 'value'}}),
        (True, {}),
        (False, {'flake': 'flake8'}),
    ],
)
def test_add_flake8_config(mocker, os, capsys, is_path_exists, params):
    mock_open = mocker.patch(
        'filecode.flake_master.utils.presets.open',
        mocker.mock_open(read_data='data\n'), create=True)
    parser = mocker.patch('filecode.flake_master.utils.presets.configparser.ConfigParser', autospec=True)
    parser().__getitem__.return_value = params

    os.path.join.return_value = 'path'
    os.path.exists.return_value = is_path_exists

    add_flake8_config([('flake', 'key')], 'path', 'filename')
    out, err = capsys.readouterr()

    if is_path_exists:
        assert out == f'\t\tUpdating {os.path.join.return_value}...\n'
        parser().add_section.assert_called_with('flake8')
    else:
        assert err == f'\t\tconfig file {os.path.join.return_value} not found\n'
        parser().write.assert_called_with(mock_open())


def test_create_preset_file(mocker, os):
    os.path.join.return_value = 'path'
    mock_open = mocker.patch(
        'filecode.flake_master.utils.presets.open',
        mocker.mock_open(read_data='data\n'),
        create=True,
    )
    json = mocker.patch('filecode.flake_master.utils.presets.json', spec=['dump'])
    preset = mocker.Mock()
    preset.name, preset.revision, preset.config_url, preset.filepath = 'name', 'revision', 'url', 'filepath'
    dump = {'name': preset.name,
            'revision': preset.revision,
            'url': preset.config_url,
            'filepath': preset.filepath}

    create_preset_file(preset, 'path', 'filename')
    json.dump.assert_called_with(dump, mock_open())


@pytest.mark.parametrize(
    'match_line_num, expected',
    [
        (0, 'coverage==5.5\npytest==6.2.2\n'),
        (1, 'safety==1.9.0\ncoverage==5.5\n'),
        (None, 'safety==1.9.0\npytest==6.2.2\ncoverage==5.5\n'),
    ],
)
def test_merge_requirements_data(mocker, match_line_num, expected):
    mocker.patch('filecode.flake_master.utils.requirements.find_requirement_in_list', return_value=match_line_num)
    raw_old_requirements = ['safety==1.9.0', 'pytest==6.2.2']
    assert merge_requirements_data(raw_old_requirements, [('coverage', '5.5')]) == expected


@pytest.mark.parametrize(
    'raw_old_requirements, parse_name, expected',
    [
        ([' #requirement '], '', None),
        (['requirement  '], 'package_name', 0),
        (['requirement  '], 'name', None),
        ([''], 'name', None),
    ],
)
def test_find_requirement_in_list(mocker, raw_old_requirements, parse_name, expected):
    requirement = mocker.patch('filecode.flake_master.utils.requirements.Requirement', spec=['parse'])
    requirement.parse().name = parse_name
    assert find_requirement_in_list('package_name', raw_old_requirements) == expected


@pytest.mark.parametrize(
    'raw_old_requirements, expected',
    [
        (['requirement'], None),
    ],
)
def test_find_requirement_in_list_with_exception(mocker, raw_old_requirements, expected):
    requirement = mocker.patch('filecode.flake_master.utils.requirements.Requirement')
    requirement.parse.side_effect = ValueError
    assert find_requirement_in_list('package_name', raw_old_requirements) == expected
