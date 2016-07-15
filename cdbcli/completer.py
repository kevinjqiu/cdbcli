import functools

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS


def _fetch_db_names(couch_server, context):
    status_code, _, response = couch_server.resource.get_json('_all_dbs')
    if status_code != 200:
        return []

    return response


def _fetch_doc_ids(couch_server, context):
    if context.current_db is None:
        return []

    return list(context.current_db)


def get_completer(couch_server, context):
    return GrammarCompleter(grammar, {
        'command': WordCompleter(COMMANDS.keys()),
        'database_name': WordCompleter(functools.partial(_fetch_db_names, couch_server, context)),
        'doc_id': WordCompleter(functools.partial(_fetch_doc_ids, couch_server, context)),
    })
