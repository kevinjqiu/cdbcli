import functools
import couchdb


COMMANDS = {}


def command_handler(command):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        COMMANDS[command] = wrapper
        return wrapper
    return decorator


@command_handler('USE')
def cmd_use(context, couch_server, operand):
    try:
        context.current_db = couch_server[operand]
    except couchdb.ResourceNotFound:
        raise RuntimeError("Database '{}' does not exist".format(operand))
