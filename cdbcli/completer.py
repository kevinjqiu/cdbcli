from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS


def _database_name_completer(couch_server, context):
    status_code, _, response = couch_server.resource.get_json('_all_dbs')
    if status_code != 200:
        raise RuntimeError(response)

    # Need to update WordCompleter so it calls a function to obtain a list of
    # words rather than a static list
    return WordCompleter(response)


def get_completer(couch_server, context):
    return GrammarCompleter(grammar, {
        'command': WordCompleter(COMMANDS.keys()),
        'database_name': _database_name_completer(couch_server, context),
    })
