import functools

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS, get_all_dbs, is_view


def fetch_db_names(environment, couch_server):
    try:
        return get_all_dbs(environment, couch_server)
    except RuntimeError:
        return []


def fetch_doc_ids(environment, couch_server):
    if environment.current_db is None:
        return []

    return list(environment.current_db)


def fetch_view_ids(environment, couch_server):
    if environment.current_db is None:
        return []

    return filter(is_view, list(environment.current_db))


def fetch_view_paths(environment, couch_server):
    view_ids = fetch_view_ids(environment, couch_server)
    if not view_ids:
        return []

    paths = []
    for view_id in view_ids:
        view_doc = environment.current_db[view_id]
        paths.extend([
            '{}:{}'.format(view_id, view_name)
            for view_name in dict(view_doc.items())['views'].keys()
        ])

    return paths


def get_completer(environment, couch_server):
    return GrammarCompleter(grammar, {
        'command': WordCompleter(COMMANDS.keys()),
        'target': WordCompleter(COMMANDS.keys()),
        'database_name': WordCompleter(functools.partial(fetch_db_names, environment, couch_server)),
        'doc_id': WordCompleter(functools.partial(fetch_doc_ids, environment, couch_server)),
        'view_doc_id': WordCompleter(functools.partial(fetch_view_ids, environment, couch_server)),
        'view_path': WordCompleter(functools.partial(fetch_view_paths, environment, couch_server)),
    })
