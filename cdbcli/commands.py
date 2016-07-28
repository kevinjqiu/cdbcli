import functools
import io
import json
import traceback
import tempfile

import couchdb
import pygments
from pygments import lexers, formatters
from collections import namedtuple
from cdbcli import utils


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


def highlight_json(json_object):
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    return pygments.highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())


def highlight_javascript(code):
    return pygments.highlight(code, lexers.JavascriptLexer(), formatters.TerminalFormatter())


def highlight_python(code):
    return pygments.highlight(code, lexers.PythonLexer(), formatters.TerminalFormatter())


def get_all_dbs(environment, couch_server):
    status_code, _, response = couch_server.resource.get_json('_all_dbs')

    if status_code != 200:
        raise RuntimeError(response)

    return response


def is_view(doc):
    return doc.startswith('_design/')


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
            environment.current_db = None
        elif database_name == '-':
            pass  # TODO: implement 'previous' database
        else:
            environment.current_db = couch_server[database_name]
    except (couchdb.ResourceNotFound, couchdb.ServerError):
        raise RuntimeError("Database '{}' does not exist".format(database_name))


@command_handler('info')
@require_current_db
def info(environment, couch_server, variables):
    """info

    Show the information of the current database.
    """
    info = environment.current_db.info()
    environment.output(highlight_json(info))


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

    environment.output(highlight_json(doc))


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
            environment.output(highlight_json(dict(result.items())))
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

    couch_server.create(database_name)
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
        'python': highlight_python,
        'javascript': highlight_javascript,
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


@command_handler('man', pattern='(?P<target>[a-zA-Z0-9-_]+)')
def man(environment, couch_server, variables):
    """man <command>

    Show help for the command.
    """
    command = variables.get('target')
    command_handler = COMMANDS.get(command)
    if not command_handler:
        raise RuntimeError('Command {} not recognized'.format(command))

    if not command_handler.help:
        environment.output('No manual entry for {}'.format(command))
        return

    environment.output('')
    environment.output(command_handler.help)
    environment.output('')


@command_handler('exit')
def exit(environment, couch_server, variables):
    """exit

    Quit cdbcli.
    """
    raise EOFError()


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
        with io.open(file_path, 'w', encoding='utf8') as fh:
            json.dump(doc, fh, sort_keys=True, indent=4)

    success = environment.cli.run_in_terminal(lambda: utils.open_file_in_editor(file_path))
    if not success:
        return  # abort

    try:
        with io.open(file_path, 'r', encoding='utf8') as fh:
            json_doc = json.load(fh)

        if mode == 'edit':
            del json_doc['_rev']

        environment.current_db.save(json_doc)
    except Exception as e:
        raise RuntimeError(str(e))
