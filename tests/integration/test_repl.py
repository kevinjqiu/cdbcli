import functools
import io
import json
import tempfile
import pytest
import retrying

from unittest.mock import Mock

from cdbcli.repl import eval_, Repl
from cdbcli.commands import command_handler, COMMANDS
from tests.integration.fixtures import *  # noqa


def _get_output(environment):
    environment.output_stream.seek(0)
    return environment.output_stream.read()


@retrying.retry(stop_max_delay=10000, wait_fixed=1000)
def _get_pipe_output(pipe_output_temp_file_path, expect_empty_output=False):  # pragma: nocover
    with io.open(pipe_output_temp_file_path, 'r') as f:
        output = f.readlines()
        if expect_empty_output:
            assert len(output) == 0
        else:
            assert len(output) != 0
        return output


def _assert_command_requires_current_db(command, environment, couch_server):
    with pytest.raises(RuntimeError) as e:
        eval_(environment, couch_server, command)
    assert str(e.value) == 'No database selected.'


for command in ['exec blah', 'lv blah', 'vim blah', 'touch blah', 'info', 'cat blah', 'rm blah']:
    test_name = 'test_requires_current_db_for_command_{}'.format(command.replace(' ', '_'))
    globals()[test_name] = functools.partial(_assert_command_requires_current_db, command)


def test_non_admin_cannot_access_users(environment, non_admin_couch_server):
    eval_(environment, non_admin_couch_server, 'cd _users')
    with pytest.raises(RuntimeError) as e:
        eval_(environment, non_admin_couch_server, 'ls')
    assert 'Permission denied' == str(e.value)


def test_command_alias(environment, couch_server):
    @command_handler('abc', aliases=['duh', 'huh'])
    def abc(environment, couch_server):
        """Blah blah"""
        pass  # pragma: nocover

    assert 'abc' in COMMANDS
    handler = COMMANDS['abc']
    assert 'duh' in COMMANDS
    assert 'huh' in COMMANDS
    assert handler is COMMANDS['duh'] is COMMANDS['huh']


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


def test_cd_dash_switches_root_and_database(environment, couch_server):
    environment.current_db = couch_server.create('test')
    eval_(environment, couch_server, 'cd -')
    assert environment.current_db is None
    assert environment.previous_db.name == 'test'
    eval_(environment, couch_server, 'cd -')
    assert environment.current_db.name == 'test'
    assert environment.previous_db is None


def test_cd_dash_switches_databases(environment, couch_server):
    environment.current_db = couch_server.create('test1')
    environment.current_db = couch_server.create('test2')
    eval_(environment, couch_server, 'cd test1')
    assert environment.current_db.name == 'test1'
    eval_(environment, couch_server, 'cd test2')
    assert environment.current_db.name == 'test2'
    eval_(environment, couch_server, 'cd -')
    assert environment.current_db.name == 'test1'
    assert environment.previous_db.name == 'test2'
    eval_(environment, couch_server, 'cd -')
    assert environment.current_db.name == 'test2'
    assert environment.previous_db.name == 'test1'


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


def test_mkdir_raises_exception_for_non_admin(environment, non_admin_couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, non_admin_couch_server, 'mkdir blah')


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
    environment.output = Mock()
    eval_(environment, couch_server, 'exec _design/users:by_lastname')
    highlighted = [json.loads(c[0][0]) for c in environment.output.call_args_list]

    expected = set(['washington', 'jefferson', 'adams'])
    actual = set([x['key'] for x in highlighted])
    assert expected == actual


def test_lv_requires_real_view_doc_id(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_design_doc())
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'lv _design/blah')


def test_lv_lists_views_inside_view_doc(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_design_doc())
    environment.current_db = db
    eval_(environment, couch_server, 'lv _design/users')
    # TODO: assert map function is displayed


def test_lv_no_view(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_empty_design_doc())
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'lv _design/empty')


def test_man_unrecognized_command(environment, couch_server):
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'man xyz')


def test_man_command_has_no_help(environment, couch_server):
    @command_handler('xyz')
    def xyz(*args, **kwargs):  # pragma: nocover
        pass

    eval_(environment, couch_server, 'man xyz')
    output = _get_output(environment)
    assert 'No manual entry for xyz' == output.strip()


def test_man_command_has_help(environment, couch_server):
    @command_handler('xyz')
    def xyz(*args, **kwargs):
        """Blah blah"""

    eval_(environment, couch_server, 'man xyz')
    output = _get_output(environment)
    assert 'Blah blah' == output.strip()


def test_man_command_shows_all_help(environment, couch_server):
    eval_(environment, couch_server, 'man')
    output = _get_output(environment)
    for command, handler in COMMANDS.items():
        assert handler.help in output


def _setup_edit_environment(environment, couch_server, mocker, file_content):
    mkstemp_return = tempfile.mkstemp()
    db = couch_server.create('test')
    environment.current_db = db
    tmp = mocker.patch('cdbcli.commands.tempfile.mkstemp')
    tmp.return_value = mkstemp_return
    environment.cli = Mock()
    with io.open(tmp.return_value[1], 'w') as f:
        f.write(file_content)


def test_edit_creates_document_if_doc_id_not_exists(environment, couch_server, mocker):
    doc = {"firstName": "willy", "lastName": "wonka"}
    _setup_edit_environment(environment, couch_server, mocker, json.dumps(doc))
    eval_(environment, couch_server, 'vim ww')

    assert environment.current_db['ww'] is not None
    assert environment.current_db['ww'].get('firstName') == doc['firstName']
    assert environment.current_db['ww'].get('lastName') == doc['lastName']


def test_edit_updates_document_if_doc_id_exists(environment, couch_server, mocker):
    doc = {"firstName": "willy", "lastName": "wonka"}
    _setup_edit_environment(environment, couch_server, mocker, json.dumps(doc))
    mocker.patch('cdbcli.commands._save_doc_to_file')
    environment.current_db.save({'_id': 'ww', 'firstName': 'Walt', 'lastName': 'White'})
    eval_(environment, couch_server, 'vim ww')

    assert environment.current_db['ww'] is not None
    assert environment.current_db['ww'].get('firstName') == doc['firstName']
    assert environment.current_db['ww'].get('lastName') == doc['lastName']


def test_edit_fails_if_doc_is_not_json(environment, couch_server, mocker):
    _setup_edit_environment(environment, couch_server, mocker, 'this is not json')
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'vim ww')


def test_rm_removes_the_document(environment, couch_server):
    db = couch_server.create('test')
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('george', 'washington'),
                                   ('thomas', 'jefferson'),
                                   ('john', 'adams')]
     ]
    environment.current_db = db
    eval_(environment, couch_server, 'rm george.washington')
    assert environment.current_db is db
    output = _get_output(environment)
    assert 'Deleted document george.washington' == output.strip()


def test_rm_raises_exception_if_doc_not_found(environment, couch_server):
    db = couch_server.create('test')
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('george', 'washington'),
                                   ('thomas', 'jefferson'),
                                   ('john', 'adams')]
     ]
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'rm john.smith')


def test_rm_raises_exception_if_no_doc_provided(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    with pytest.raises(RuntimeError):
        eval_(environment, couch_server, 'rm')


def test_pipe_commands_one_pipe(environment, couch_server):
    db = couch_server.create('test')
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('william', 'shakespear'),
                                   ('william', 'shatner'),
                                   ('bill', 'gates')]
     ]
    environment.current_db = db
    _, file_path = tempfile.mkstemp()
    with io.open(file_path, 'w') as f:
        environment.output_stream = f
        eval_(environment, couch_server, 'ls | grep william')

    output = _get_pipe_output(file_path)
    assert {'d william.shakespear', 'd william.shatner'} == set(map(str.strip, output))


def test_pipe_commands_multiple_pipes(environment, couch_server):
    db = couch_server.create('test')
    [db.save(get_user_doc(first_name, last_name))
     for first_name, last_name in [('william', 'shakespear'),
                                   ('william', 'shatner'),
                                   ('bill', 'gates')]
     ]
    environment.current_db = db
    _, file_path = tempfile.mkstemp()
    with io.open(file_path, 'w') as f:
        environment.output_stream = f
        eval_(environment, couch_server, 'ls | cut -d " " -f 2 | cut -d "." -f 1 | sort | uniq')

    output = _get_pipe_output(file_path)
    assert {'william', 'bill'} == set(map(str.strip, output))


def test_pipe_error(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    _, file_path = tempfile.mkstemp()
    with io.open(file_path, 'w') as f:
        environment.output_stream = f
        with pytest.raises(RuntimeError):
            eval_(environment, couch_server, 'ls | command_not_found')
        # environment.output_stream should be reverted to its original state
        # if anything in the pipe fails
        assert environment.output_stream is f


def test_du_command_no_database_selected(environment, couch_server):
    couch_server.create('test')
    eval_(environment, couch_server, 'du')
    output = _get_output(environment).splitlines()
    assert '_replicator' in output[0]
    assert '_users' in output[1]
    assert 'test' in output[2]


def test_du_command_with_database_selected(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    _, file_path = tempfile.mkstemp()
    eval_(environment, couch_server, 'du')
    output = _get_output(environment)
    assert 'test' in output


def test_touch_requires_doc_id(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    with pytest.raises(RuntimeError) as e:
        eval_(environment, couch_server, 'touch ')
    assert str(e.value) == 'Must specify doc_id'


def test_touch_creates_empty_doc(environment, couch_server):
    db = couch_server.create('test')
    environment.current_db = db
    eval_(environment, couch_server, 'touch finding_nemo')
    assert db['finding_nemo'] is not None
    assert {'_id', '_rev'} == set(db['finding_nemo'].keys())


def test_repl_prompt_non_admin(environment, non_admin_couch_server):
    config = Mock(username='None', host='localhost', database=None)
    repl = Repl(non_admin_couch_server, config, environment)
    assert 'None@localhost/ $ ' == repl.prompt


def test_repl_prompt_admin(environment, couch_server):
    config = Mock(username='admin', host='localhost', database=None)
    repl = Repl(non_admin_couch_server, config, environment)
    assert 'admin@localhost/ # ' == repl.prompt
