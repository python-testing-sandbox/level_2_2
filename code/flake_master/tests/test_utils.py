import json

import pytest
from unittest.mock import Mock, mock_open

from code.flake_master.utils.presets import (
    extract_preset_url, extract_preset_file_path, extract_preset_credentials,
    fetch_preset, create_preset_file,  add_flake8_config, add_packages_to_requirements_file,
    apply_preset_to_path)
from code.flake_master.utils.preset_fetchers import (
    parse_preset_from_str_config, load_preset_from_url, load_preset_from_file)
from code.flake_master.utils.requirements import merge_requirements_data, find_requirement_in_list


@pytest.mark.parametrize(
    'preset_name_or_url_or_path, preset_info, presets_repo_url, expected',
    [
        ('http://yandex.ru', None, 'http://repo.ru', 'http://yandex.ru'),
        ('preset_name', None, 'http://repo.ru', 'http://repo.ru/master/presets/preset_name.cfg'),
        ('preset_name', {'url': 'http://yandex.ru'}, 'http://repo.ru', 'http://yandex.ru'),
    ]
)
def test_extract_preset_url(preset_name_or_url_or_path, presets_repo_url, preset_info, expected):
    assert extract_preset_url(preset_name_or_url_or_path, preset_info, presets_repo_url) == expected


@pytest.mark.parametrize(
    'preset_name_or_url_or_path, preset_info, is_path_exists, expected',
    [
        ('preset_name.cfg', None, True, 'presets/preset_name.cfg'),
        ('preset_name.cfg', {'filepath': 'any/file/path'}, True, 'any/file/path'),
        (None, {'filepath': 'any/file/path'}, True, 'any/file/path'),
        ('preset_name.txt', None, True, None),
        ('preset_name.cfg', None, False, None),
        (None, None, False, None),
    ]
)
def test_extract_preset_file_path(mocker, preset_name_or_url_or_path, preset_info, is_path_exists, expected):
    mocker.patch('os.path.exists', Mock(return_value=is_path_exists))
    mocker.patch('os.path.abspath', Mock(return_value=expected))

    assert extract_preset_file_path(preset_name_or_url_or_path, preset_info) == expected


@pytest.mark.parametrize(
    'preset_name_or_url_or_path, preset_info, presets_repo_url, is_path_exists, expected',
    [
        ('http://yandex.ru', None, 'http://repo.ru', True, (None, 'http://yandex.ru')),
        ('preset_name', None, 'http://repo.ru', False, (None, 'http://repo.ru/master/presets/preset_name.cfg')),
        (
            'http://yandex.ru', {'url': 'http://ya.ru', 'filepath': 'any/file/path'},
            'http://repo.ru', False, ('any/file/path', 'http://ya.ru'),
        ),
    ]
)
def test_extract_preset_credentials(
    mocker, preset_name_or_url_or_path, preset_info,
    presets_repo_url, is_path_exists, expected,
):
    mocker.patch('os.path.exists', Mock(return_value=is_path_exists))
    mocker.patch('os.path.abspath', Mock(return_value=expected[0] or 'any path'))

    assert extract_preset_credentials(preset_name_or_url_or_path, preset_info, presets_repo_url) == expected


def test_parse_preset_from_str_config(flake8_preset_factory, row_config_data):
    url = 'any url'
    filepath = None
    expected = flake8_preset_factory(config_url=url)
    assert parse_preset_from_str_config(row_config_data, filepath, url) == expected


def test_load_preset_from_url(mocker, flake8_preset_factory, row_config_data):
    response = mocker.patch('code.flake_master.utils.preset_fetchers.get', autospec=True)
    url = 'any url'
    response(url).text = row_config_data
    expected = flake8_preset_factory(config_url=url)

    assert load_preset_from_url(url) == expected


def test_load_preset_from_file(mocker, row_config_data, flake8_preset_factory):
    mocker.patch('code.flake_master.utils.preset_fetchers.open', mock_open(read_data=row_config_data))
    filepath = 'any path'
    expected = flake8_preset_factory(filepath=filepath)

    assert load_preset_from_file(filepath) == expected


@pytest.mark.parametrize(
    'preset_file_path, preset_url',
    [
        ('home/any/path', 'http://yandex.ru'),
        ('home/any/path', None),
        (None, 'http://yandex.ru'),
        (None, None),
    ]
)
def test_fetch_preset(mocker, preset_file_path, preset_url, flake8_preset_factory):
    expected = None
    if preset_file_path or preset_url:
        expected = flake8_preset_factory(filepath=preset_file_path, config_url=preset_url)

    mocker.patch(
        'code.flake_master.utils.presets.extract_preset_credentials',
        Mock(return_value=(preset_file_path, preset_url)),
    )
    mocker.patch('code.flake_master.utils.presets.load_preset_from_file', Mock(return_value=expected))
    mocker.patch('code.flake_master.utils.presets.load_preset_from_url', Mock(return_value=expected))

    assert fetch_preset(presets_repo_url='any url') == expected


@pytest.mark.parametrize(
    'package_name, raw_old_requirements, expected',
    [
        ('flake8', ['flake==3.8.4', 'flake7==3.8.4', '  flake8==3.8.4  '], 2),
        ('flake8', ['flake==3.8.4', '', '#flake8==3.8.4'], None),
    ]
)
def test_find_requirement_in_list(package_name, raw_old_requirements, expected):
    assert find_requirement_in_list(package_name, raw_old_requirements) == expected


def test_find_requirement_in_list_raises_value_error(mocker):
    mocker.patch('code.flake_master.utils.requirements.Requirement.parse', Mock(side_effect=ValueError))
    package_name = 'flake8'
    raw_old_requirements = ['flake7==3.8.4', 'flake7==3.8.4', '#flake8==3.8.4']
    assert not find_requirement_in_list(package_name, raw_old_requirements)


@pytest.mark.parametrize(
    'raw_old_requirements, flake8_plugins, expected',
    [
        (['flake==3.6', 'flake8==3.8'], [('flake8', '5.3')], 'flake==3.6\nflake8==5.3\n'),
        (['flake==3.6', 'flake8==3.8'], [('flake7', '5.3')], 'flake==3.6\nflake8==3.8\nflake7==5.3\n'),
        (['flake7==3.6'], [('flake7', '5.3'), ('flake8', '3.8')], 'flake7==5.3\nflake8==3.8\n'),
    ]
)
def test_merge_requirements_data(raw_old_requirements, flake8_plugins, expected):
    assert merge_requirements_data(raw_old_requirements, flake8_plugins) == expected


def test_create_preset_file(mocker, flake8_preset_factory, tmpdir):
    flake8_preset = flake8_preset_factory()
    expected = json.dumps({
            'name': flake8_preset.name,
            'revision': flake8_preset.revision,
            'url': flake8_preset.config_url,
            'filepath': flake8_preset.filepath,
            })

    any_file = tmpdir.join('hello.txt')
    mocker.patch('os.path.join', Mock(return_value=any_file.strpath))
    create_preset_file(flake8_preset, 'any', 'path')

    assert any_file.read() == expected


@pytest.mark.parametrize(
    'is_path_exists, has_flake8_section',
    [
        (False, True),
        (False, False),
        (True, True),
        (True, False),
    ]
)
def test_add_flake8_config(mocker, tmpdir, capsys, is_path_exists, row_config_data, has_flake8_section):
    flake8_config = [('par', 'val'), ('par1', 'val1')]
    flake8_section_name = 'flake8'
    flake8_config_row = '\n'.join(f'{p} = {v}' for (p, v) in flake8_config) + '\n\n'

    if has_flake8_section:
        row_config_data = f'{row_config_data}[{flake8_section_name}]\npar3 = val3\n'

    config_file = tmpdir.join('hello.ini')
    config_file.write(row_config_data)

    mocker.patch('os.path.exists', Mock(return_value=is_path_exists))
    mocker.patch('os.path.join', Mock(return_value=config_file.strpath))

    add_flake8_config(flake8_config, 'any', 'path', flake8_section_name)
    captured = capsys.readouterr()

    if is_path_exists:
        assert captured.out == f'\t\tUpdating {config_file.strpath}...\n'
        assert config_file.read() == (
            f'{row_config_data}{flake8_config_row}' if has_flake8_section
            else f'{row_config_data}[{flake8_section_name}]\n{flake8_config_row}'
        )
    else:
        assert captured.err == f'\t\tconfig file {config_file.strpath} not found\n'
        assert config_file.read() == f'[{flake8_section_name}]\n{flake8_config_row}'


@pytest.mark.parametrize(
    'requirements_files_names, is_path_exists',
    [
        (['req.txt', 'req1.txt'], True),
        (['req.txt', 'req1.txt'], False),
    ]
)
def test_add_packages_to_requirements_file(
    mocker, requirements_files_names,
    is_path_exists, tmpdir, capsys,
):
    default_requirements_file_name = 'any_name.txt'
    flake8_plugins = [('flake7', '5.3'), ('flake8', '3.8')]
    raw_old_requirements = 'flake==3.8.4\nflake7==3.8.4\nflake8==3.8.4\n'

    req_file = tmpdir.join('requirements.txt')
    req_file.write(raw_old_requirements)
    mocker.patch('os.path.join', Mock(return_value=req_file.strpath))
    mocker.patch('os.path.exists', Mock(return_value=is_path_exists))

    add_packages_to_requirements_file(flake8_plugins, 'df', requirements_files_names, default_requirements_file_name)
    captured = capsys.readouterr()

    if is_path_exists:
        assert captured.out == f'\t\tadding to {req_file.strpath}...\n'
        assert req_file.read() == 'flake==3.8.4\nflake7==5.3\nflake8==3.8\n'
    else:
        assert captured.out == f'\t\tcreating {default_requirements_file_name}...\n'
        assert req_file.read() == 'flake7==5.3\nflake8==3.8'


def test_apply_preset_to_path(capsys, mocker, flake8_preset_factory):
    mocker.patch('code.flake_master.utils.presets.add_packages_to_requirements_file')
    mocker.patch('code.flake_master.utils.presets.add_flake8_config')
    mocker.patch('code.flake_master.utils.presets.create_preset_file')

    flake8_preset = flake8_preset_factory()
    apply_preset_to_path(flake8_preset, 'path', 'name')
    captured = capsys.readouterr()

    assert captured.out == '\tAdding 3 requirements...\n\tCreating flake8 config...\n\tCreating preset file...\n'
