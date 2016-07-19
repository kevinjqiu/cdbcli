import pytest

from cdbcli.repl import eval_
from fixtures import *  # noqa


def _get_output(environment):
    environment.output_stream.seek(0)
    return environment.output_stream.read()


def _get_mock_highlight(mocker):
    mock_highlight = mocker.patch('cdbcli.commands.highlight')
    mock_highlight.return_value = ''
    return mock_highlight


def _get_highlighted(mock_highlight):
    args = [
        c[0][0]
        for c in mock_highlight.call_args_list
    ]
    return args


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


def test_cd_dotdot_change_to_root_dir(environment, couch_server):
    environment.current_db = couch_server.create('test')
    eval_(environment, couch_server, 'cd ..')
    assert environment.current_db is None


def test_cd_slash_change_to_root_dir(environment, couch_server):
    environment.current_db = couch_server.create('test')
    eval_(environment, couch_server, 'cd /')
    assert environment.current_db is None


def test_cd_dotdot_does_not_change_db_if_already_root(environment, couch_server):
    eval_(environment, couch_server, 'cd ..')
    assert environment.current_db is None


def test_cd_slash_does_not_change_db_if_already_root(environment, couch_server):
    eval_(environment, couch_server, 'cd /')
    assert environment.current_db is None


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
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('george', 'washington'),
                                   ('thomas', 'jefferson'),
                                   ('john', 'adams')]
     ]
    db.save(get_user_design_doc())
    environment.current_db = db
    eval_(environment, couch_server, 'ls')
    assert environment.current_db is db
    output = _get_output(environment).splitlines()
    expected = set(['v _design/users',
                    'd george.washington',
                    'd thomas.jefferson',
                    'd john.adams'])
    assert expected == set(output)


def test_cat_raises_error_when_no_docid_specified(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'cat')


def test_cat_raises_error_when_no_current_db_selected(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'cat cafebabe')


def test_cat_raises_error_when_no_doc_matching_id(environment, couch_server):
    db = couch_server.create('test')
    doc_id, _ = db.save({})
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'cat cafebabe')


def test_cat_shows_doc_content(environment, couch_server):
    db = couch_server.create('test')
    doc_id, _ = db.save({})
    environment.current_db = db
    eval_(environment, couch_server, 'cat {}'.format(doc_id))
    output = _get_output(environment)
    assert doc_id in output


def test_exit_raises_eof_error(environment, couch_server):
    with pytest.raises(EOFError):
        eval_(environment, couch_server, 'exit')


def test_mkdir_raises_error_when_db_already_exists(environment, couch_server):
    couch_server.create('test')
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'mkdir test')


def test_mkdir_raises_error_when_creating_db_inside_a_db(environment, couch_server):
    environment.current_db = couch_server.create('test')
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'mkdir test_1')


def test_mkdir_creates_new_database(environment, couch_server):
    eval_(environment, couch_server, 'mkdir test')
    assert couch_server['test'] is not None
    output = _get_output(environment)
    assert 'Created test' in output


def test_exec_requires_current_db(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'exec blah')


def test_exec_view_does_not_exist(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_design_doc())
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'exec _design/users')


def test_exec_view(environment, couch_server, mocker):
    db = couch_server.create('test')
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('george', 'washington'),
                                   ('thomas', 'jefferson'),
                                   ('john', 'adams')]
     ]
    db.save(get_user_design_doc())
    environment.current_db = db
    mock_highlight = _get_mock_highlight(mocker)
    eval_(environment, couch_server, 'exec _design/users/_view/by_lastname')
    highlighted = _get_highlighted(mock_highlight)
    expected = set(['washington', 'jefferson', 'adams'])
    actual = set([x['key'] for x in highlighted])
    assert expected == actual
