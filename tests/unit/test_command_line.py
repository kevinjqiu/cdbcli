import cdbcli.main as cdbcli_main
from cdbcli import __version__


def test_version_prints_correct_version():
    assert __version__ in cdbcli_main.get_version()


def test_main_with_version_toggle(mocker):
    exit_mock = mocker.patch('click.core.Context.exit')
    get_version_mock = mocker.patch('cdbcli.main.get_version')
    cdbcli_main.main(['--version'])
    assert 1 == get_version_mock.call_count
    assert 1 == exit_mock.call_count
