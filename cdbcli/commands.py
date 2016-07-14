import functools
import json

import couchdb
import pygments
from pygments import lexers, formatters


COMMANDS = {}


def command_handler(command, operand_pattern=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        COMMANDS[command] = (wrapper, operand_pattern)
        return wrapper
    return decorator


def require_current_db(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        assert 'context' in kwargs
        context = kwargs.get('context')
        if not context.current_db:
            raise RuntimeError('No database selected.')

        return fn(*args, **kwargs)
    return wrapper


def highlight(json_object):
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    return pygments.highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())


@command_handler('ls')
def ls(context, couch_server, variables):
    if context.current_db is None:
        status_code, _, response = couch_server.resource.get_json('_all_dbs')

        if status_code != 200:
            raise RuntimeError(response)

        for db_name in response:
            db = couch_server[db_name]
            info = db.info()
            print('{:>10} {}'.format(info['doc_count'], db_name))
    else:
        for doc in context.current_db:
            print(doc)


@command_handler('cd', '(?P<database_name>[^\s]+)')
def cd(context, couch_server, variables):
    database_name = variables.get('database_name')
    try:
        if not database_name or database_name == '/' or database_name == '..':
            context.current_db = None
        elif database_name == '-':
            pass  # TODO: implement 'previous' database
        else:
            context.current_db = couch_server[database_name]
    except couchdb.ResourceNotFound:
        raise RuntimeError("Database '{}' does not exist".format(database_name))


@command_handler('info')
@require_current_db
def info(context, couch_server, variables):
    info = context.current_db.info()
    print(highlight(info))


@command_handler('cat', '(?P<doc_id>[^\s]+)')
@require_current_db
def get(context, couch_server, variables):
    doc_id = variables.get('doc_id')
    if not doc_id:
        raise RuntimeError('Document not found')

    doc = context.current_db.get(doc_id)
    if not doc:
        raise RuntimeError('Document not found')
    print(highlight(doc))
