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


def highlight(json_object):
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    return pygments.highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())


@command_handler('USE', '(?P<database_name>[a-zA-Z0-9_-].*)')
def use(context, couch_server, variables):
    database_name = variables.get('database_name')
    try:
        if not database_name:
            context.current_db = None
        else:
            context.current_db = couch_server[database_name]
    except couchdb.ResourceNotFound:
        raise RuntimeError("Database '{}' does not exist".format(database_name))


@command_handler('SHOW STATS')
def show_stats(context, couch_server, variables):
    if not context.current_db:
        raise RuntimeError('No database selected.')

    info = context.current_db.info()
    print(highlight(info))
