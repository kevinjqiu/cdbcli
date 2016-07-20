import functools
import json
import traceback

import couchdb
import pygments
from pygments import lexers, formatters
from collections import namedtuple


COMMANDS = {}


Command = namedtuple('Command', ['handler', 'pattern', 'help'])


def command_handler(command, pattern=None, help=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        COMMANDS[command] = Command(wrapper, pattern, help)
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


@command_handler('ls', help='ls\n\nShow the documents in the current database')
def ls(environment, couch_server, variables):
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


@command_handler('cd', '(?P<database_name>[a-zA-Z0-9-_./]+)', help=('cd <dbname>\n\n',
                                                                    'Change the current database'))
def cd(environment, couch_server, variables):
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


@command_handler('info', help='info\n\nShow the information of the current database')
@require_current_db
def info(environment, couch_server, variables):
    info = environment.current_db.info()
    environment.output(highlight_json(info))


@command_handler('cat', '(?P<doc_id>[^\s]+)', help=('cat <doc_id>\n\n'
                                                    'Show the content of a document by its id'))
@require_current_db
def cat(environment, couch_server, variables):
    doc_id = variables.get('doc_id')
    if not doc_id:
        raise RuntimeError('Document not found')

    doc = environment.current_db.get(doc_id)
    if not doc:
        raise RuntimeError('Document not found')

    environment.output(highlight_json(doc))


@command_handler('exec', '(?P<view_id>[^\s]+)', help=('exec <view_path>\n\n'
                                                      'Execute the view given the full view path\n'))
@require_current_db
def exec_(environment, couch_server, variables):
    view_id = variables.get('view_id')
    if not view_id:
        raise RuntimeError('View not found')

    try:
        for result in environment.current_db.view(view_id):
            environment.output(highlight_json(dict(result.items())))
    except:
        traceback.print_exc()
        raise RuntimeError('Unable to exec view: {}'.format(view_id))


@command_handler('mkdir', '(?P<database_name>[a-zA-Z0-9-_]+)', help=('mkdir <dbname>\n\n'
                                                                     'Create a database'))
def mkdir(environment, couch_server, variables):
    if environment.current_db is not None:
        raise RuntimeError('You can only create databases from /')

    database_name = variables.get('database_name')

    if database_name in couch_server:
        raise RuntimeError('Database {} already exists'.format(database_name))

    couch_server.create(database_name)
    environment.output('Created {}'.format(database_name))


@command_handler('lv', '(?P<view_doc_id>[a-zA-Z0-9-_/]+)', help=('lv <view_doc_id>\n\n'
                                                                 'Show the views inside the view document'))
@require_current_db
def lv(environment, couch_server, variables):
    view_doc_id = variables['view_doc_id']
    if view_doc_id not in environment.current_db:
        raise RuntimeError('{} not found'.format(view_doc_id))

    view_doc = environment.current_db[view_doc_id]
    language = view_doc.get('language', 'javascript')

    highlighter = {
        'python': highlight_python,
        'javascript': highlight_javascript,
    }.get(language, lambda x: x)

    views = view_doc.get('views')
    for view_name, view_funcs in views.items():
        environment.output('{}:{}'.format(view_doc_id, view_name))
        map_func = view_funcs.get('map', '')
        reduce_func = view_funcs.get('reduce', '')
        environment.output(highlighter(map_func))
        environment.output(highlighter(reduce_func))


@command_handler('man', pattern='(?P<target>[a-zA-Z0-9-_]+)', help='Show help for command')
def man(environment, couch_server, variables):
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
    raise EOFError()
