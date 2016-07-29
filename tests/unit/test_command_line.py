from cdbcli.main import get_version
from cdbcli import __version__


def test_version_prints_correct_version():
    assert __version__ in get_version()
