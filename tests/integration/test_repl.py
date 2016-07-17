import pytest

from cdbcli.repl import eval_
from cdbcli.environment import Environment
from fixtures import *  # noqa


def test_cd_on_nonexistent_db_raises_error(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'cd test')


def test_cd_changes_current_db_in_environment(environment, couch_server):
    couch_server.create('test')
    eval_(environment, couch_server, 'cd test')
    assert environment.current_db.name == 'test'
