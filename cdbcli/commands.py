import functools
import couchdb


COMMANDS = {}


def command_handler(command, operand_pattern):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        COMMANDS[command] = (wrapper, operand_pattern)
        return wrapper
    return decorator


@command_handler('USE', '(?P<database_name>[a-zA-Z0-9_-].*)')
def cmd_use(context, couch_server, variables):
    try:
        database_name = variables.get('database_name')
        if not database_name:
            context.current_db = None
        else:
            context.current_db = couch_server[database_name]
    except couchdb.ResourceNotFound:
        raise RuntimeError("Database '{}' does not exist".format(operand))
