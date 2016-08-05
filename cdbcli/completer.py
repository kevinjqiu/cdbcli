import functools

from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS, get_all_dbs, is_view

# {{{ See https://github.com/jonathanslenders/python-prompt-toolkit/pull/344
# I modified this class to support context-aware auto-complete word list
# fetching. Once the above PR is merged and new version of prompt-toolkit
# is released, this class can be removed.
from six import string_types
from prompt_toolkit.completion import Completer, Completion


class WordCompleter(Completer):  # pragma: nocover
    """
    Simple autocompletion on a list of words.
    :param words: List of words, or a callable that produces a list of words.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-information.
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    """
    def __init__(self, words, ignore_case=False, meta_dict=None, WORD=False,
                 sentence=False, match_middle=False):
        assert not (WORD and sentence)

        if not callable(words):
            assert all(isinstance(w, string_types) for w in words)
            self.fetch_words = lambda: list(words)  # noqa
        else:
            self.fetch_words = words
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle

    @property
    def words(self):
        return self.fetch_words()

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(WORD=self.WORD)

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matches(word):
            """ True when the word before the cursor matches. """
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        for a in self.words:
            if word_matches(a):
                display_meta = self.meta_dict.get(a, '')
                yield Completion(a, -len(word_before_cursor), display_meta=display_meta)
# }}}


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
