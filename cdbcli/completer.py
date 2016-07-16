import functools

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS, get_all_dbs, is_view


def _fetch_db_names(environment, couch_server):
    try:
        return get_all_dbs(environment, couch_server)
    except RuntimeError:
        return []


def _fetch_doc_ids(environment, couch_server):
    if environment.current_db is None:
        return []

    return list(environment.current_db)


def _fetch_view_ids(environment, couch_server):
    if environment.current_db is None:
        return []

    paths = []
    for view_id in filter(is_view, list(environment.current_db)):
        view_doc = environment.current_db[view_id]
        paths.extend([
            '{}/_view/{}'.format(view_id, view_name)
            for view_name in dict(view_doc.items())['views'].keys()
        ])

    return paths

def get_completer(environment, couch_server):
    return GrammarCompleter(grammar, {
        'command': WordCompleter(COMMANDS.keys()),
        'database_name': WordCompleter(functools.partial(_fetch_db_names, environment, couch_server)),
        'doc_id': WordCompleter(functools.partial(_fetch_doc_ids, environment, couch_server)),
        'view_id': WordCompleter(functools.partial(_fetch_view_ids, environment, couch_server)),
    })
