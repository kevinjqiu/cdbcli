import functools
import io
import json
import traceback
import tempfile

import couchdb
from collections import namedtuple
from cdbcli import utils, highlighters


COMMANDS = {}


Command = namedtuple('Command', ['handler', 'pattern', 'help'])


def command_handler(command, pattern=None, aliases=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        COMMANDS[command] = Command(wrapper, pattern, fn.__doc__)
        for alias in (aliases or []):
            COMMANDS[alias] = COMMANDS[command]
        return wrapper
    return decorator


def require_current_db(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        assert 'environment' in kwargs
        environment = kwargs.get('environment')
        if not environment.current_db:
            raise RuntimeError('No database selected.')

        return fn(*args, **kwargs)
    return wrapper


def get_all_dbs(environment, couch_server):
    status_code, _, response = couch_server.resource.get_json('_all_dbs')

    if status_code != 200:
        raise RuntimeError(response)

    return response


def is_view(doc):
    return doc.startswith('_design/')


def json_dumps(json_object):
    return json.dumps(json_object, sort_keys=True, indent=4)


@command_handler('ls')
def ls(environment, couch_server, variables):
    """ls

    Show the documents in the current database.
    """
    if environment.current_db is None:
        all_dbs = get_all_dbs(environment, couch_server)

        for db_name in all_dbs:
            db = couch_server[db_name]
            info = db.info()
            environment.output('{:>10} {}'.format(info['doc_count'], db_name))
    else:
        for doc in environment.current_db:
            type_ = 'd' if not is_view(doc) else 'v'
            environment.output('{} {}'.format(type_, doc))


@command_handler('cd', '(?P<database_name>[a-zA-Z0-9-_./]+)')
def cd(environment, couch_server, variables):
    """cd <database_name>

    Change the current database
    """
    database_name = variables.get('database_name')
    try:
        if not database_name or database_name == '/' or database_name == '..':
            environment.current_db, environment.previous_db = None, environment.current_db
        elif database_name == '-':
            environment.current_db, environment.previous_db = environment.previous_db, environment.current_db
        else:
            environment.current_db, environment.previous_db = couch_server[database_name], environment.current_db
    except (couchdb.ResourceNotFound, couchdb.ServerError):
        raise RuntimeError("Database '{}' does not exist".format(database_name))


@command_handler('info')
@require_current_db
def info(environment, couch_server, variables):
    """info

    Show the information of the current database.
    """
    info = environment.current_db.info()
    environment.output(json_dumps(info), highlighters.json)


@command_handler('cat', '(?P<doc_id>[^\s]+)')
@require_current_db
def cat(environment, couch_server, variables):
    """cat <doc_id>

    Show the content of a document by its id.
    """
    doc_id = variables.get('doc_id')
    if not doc_id:
        raise RuntimeError('Document not found')

    doc = environment.current_db.get(doc_id)
    if not doc:
        raise RuntimeError('Document not found')

    environment.output(json_dumps(doc), highlighters.json)


@command_handler('rm', '(?P<doc_id>[^\s]+)')
@require_current_db
def rm(environment, couch_server, variables):
    """rm <doc_id>

    Removes the document by its id.
    """
    doc_id = variables.get('doc_id')
    if not doc_id:
        raise RuntimeError('Document not found')

    doc = environment.current_db.get(doc_id)
    if not doc:
        raise RuntimeError('Document not found')

    environment.current_db.delete(doc)

    environment.output('Deleted document {} '.format(doc_id))


@command_handler('exec', '(?P<view_path>[^\s]+)')
@require_current_db
def exec_(environment, couch_server, variables):
    """exec <view_path>

    Execute the view given the full view path.
    """
    view_path = variables.get('view_path')
    if ':' not in view_path:
        raise RuntimeError('Invalid view_path. Must be of the form: view_doc_id:view_name')
    view_id, view_name = view_path.split(':', 1)
    if not view_id:
        raise RuntimeError('View not found')

    try:
        for result in environment.current_db.view('{}/_view/{}'.format(view_id, view_name)):
            environment.output(json_dumps(dict(result.items())), highlighters.json)
    except:
        traceback.print_exc()
        raise RuntimeError('Unable to exec view: {}'.format(view_id))


@command_handler('mkdir', '(?P<database_name>[a-zA-Z0-9-_]+)')
def mkdir(environment, couch_server, variables):
    """mkdir <database_name>

    Create a database
    """
    if environment.current_db is not None:
        raise RuntimeError('You can only create databases from /')

    database_name = variables.get('database_name')

    if database_name in couch_server:
        raise RuntimeError('Database {} already exists'.format(database_name))

    try:
        couch_server.create(database_name)
    except couchdb.Unauthorized as e:
        raise RuntimeError(str(e))
    environment.output('Created {}'.format(database_name))


@command_handler('lv', '(?P<view_doc_id>[a-zA-Z0-9-_/]+)')
@require_current_db
def lv(environment, couch_server, variables):
    """lv <view_doc_id>

    Show the views inside the view document.
    """
    view_doc_id = variables['view_doc_id']
    if view_doc_id not in environment.current_db:
        raise RuntimeError('{} not found'.format(view_doc_id))

    view_doc = environment.current_db[view_doc_id]
    language = view_doc.get('language', 'javascript')

    highlighter = {
        'python': highlighters.python,
        'javascript': highlighters.javascript,
        None: lambda x: x
    }.get(language)

    views = view_doc.get('views')

    if not views:
        raise RuntimeError("The design doc {} doesn't have any views".format(view_doc_id))

    for view_name, view_funcs in views.items():
        environment.output('{}:{}'.format(view_doc_id, view_name))
        map_func = view_funcs.get('map', '')
        reduce_func = view_funcs.get('reduce', '')
        environment.output(highlighter(map_func))
        environment.output(highlighter(reduce_func))


@command_handler('man', pattern='(?P<target>[a-zA-Z0-9-_]*)', aliases=['help'])
def man(environment, couch_server, variables):
    """man <command>

    Show help for the command.
    """
    command = variables.get('target')

    if not command:
        commands = COMMANDS.keys()
    else:
        commands = [command]

    for command in commands:
        command_handler = COMMANDS.get(command)
        if not command_handler:
            raise RuntimeError('Command {} not recognized'.format(command))

        if not command_handler.help:
            environment.output('No manual entry for {}'.format(command))
            return

        environment.output(command_handler.help)


@command_handler('exit')
def exit(environment, couch_server, variables):
    """exit

    Quit cdbcli.
    """
    raise EOFError()


def _convert_bytes_to_human_readable(size_in_bytes):
    units = ['byte', 'KB', 'MB', 'GB', 'TB']
    unit_step = 0
    memory_amount = float(size_in_bytes)
    while memory_amount > 1024 and unit_step < len(units):
        memory_amount /= 1024.0
        unit_step += 1

    return '{:.2f} {}s'.format(memory_amount, units[unit_step])


@command_handler('du')
def du(environment, couch_server, variables):
    """du

    Shows the number of documents and amount of disk space they take up.
    """
    databases = [environment.current_db]

    if not environment.current_db:
        db_names = couch_server.resource.get_json('_all_dbs')[2]
        databases = [couch_server[db] for db in db_names]

    for database in databases:
        db_info = database.info()

        # Refer to http://docs.couchdb.org/en/latest/api/database/common.html#get--db
        docs_in_db = db_info['doc_count']
        total_usage = _convert_bytes_to_human_readable(db_info['disk_size'])
        environment.output('{:<16}{:<24}({} documents)'.format(total_usage, database.name, docs_in_db))

    environment.output('')


def _save_doc_to_file(file_path, doc):
    with io.open(file_path, 'w', encoding='utf8') as fh:
        json.dump(doc, fh, sort_keys=True, indent=4)


def _load_doc_from_file(file_path):
    with io.open(file_path, 'r', encoding='utf8') as fh:
        return json.load(fh)


@command_handler('vim', pattern='(?P<doc_id>[^\s]+)', aliases=['vi', 'emacs', 'ed'])
@require_current_db
def edit(environment, couch_server, variables):
    """vim|vi|emacs|ed <doc_id>

    Open an external $EDITOR to edit or create a new document

    When <doc_id> exists, the text editor is open with the existing doc for editing.
    When <doc_id> doesn't exist, the text editor is open with a blank document for creation.

    Note: it doesn't matter which command you use, vi, emacs or ed, it will only use your $EDITOR
    """
    doc_id = variables.get('doc_id')
    mode = 'create' if doc_id not in environment.current_db else 'edit'

    _, file_path = tempfile.mkstemp('.json')
    if mode == 'edit':
        doc = environment.current_db[doc_id]
        safe_doc = dict(doc)
        safe_doc.pop('_rev', None)
        safe_doc.pop('_id', None)
        _save_doc_to_file(file_path, safe_doc)

    success = environment.run_in_terminal(lambda: utils.open_file_in_editor(file_path))

    if not success:
        return  # abort

    try:
        updated_doc = _load_doc_from_file(file_path)

        if mode == 'edit':
            updated_doc.pop('_rev', None)
            updated_doc.pop('_id', None)
            for key, value in updated_doc.items():
                doc[key] = value
            environment.current_db.save(doc)
        else:
            environment.current_db[doc_id] = updated_doc
    except Exception as e:
        raise RuntimeError(str(e))
