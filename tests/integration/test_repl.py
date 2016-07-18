import pytest

from cdbcli.repl import eval_
from cdbcli.environment import Environment
from fixtures import *  # noqa


def _get_output(environment):
    environment.output_stream.seek(0)
    return environment.output_stream.read()


def test_info_command_raises_error_when_no_current_db(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'info')


def test_info_command_show_db_stats(environment, couch_server):
    environment.current_db = couch_server.create('test')
    eval_(environment, couch_server, 'info')
    output = _get_output(environment)
    assert 'doc_count' in output


def test_cd_on_nonexistent_db_raises_error(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'cd test')


def test_cd_changes_current_db_in_environment(environment, couch_server):
    couch_server.create('test')
    eval_(environment, couch_server, 'cd test')
    assert environment.current_db.name == 'test'


def test_ls_shows_all_dbs_if_no_current_db(environment, couch_server):
    eval_(environment, couch_server, 'ls')
    assert environment.current_db is None
    output = _get_output(environment).splitlines()
    assert 2 == len(output)
    assert '_replicator' in output[0]
    assert '_users' in output[1]


def test_ls_shows_no_doc_if_no_doc(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    eval_(environment, couch_server, 'ls')
    assert environment.current_db is db
    output = _get_output(environment).splitlines()
    assert 0 == len(output)


def test_ls_shows_all_docs_if_current_db_is_set(environment, couch_server):
    db = couch_server.create('test')
    docs = [db.save({}) for _ in xrange(10)]
    environment.current_db = db
    eval_(environment, couch_server, 'ls')
    assert environment.current_db is db
    output = _get_output(environment).splitlines()
    assert 10 == len(output)
