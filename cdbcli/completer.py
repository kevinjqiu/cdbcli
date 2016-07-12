from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar


completer = GrammarCompleter(grammar, {
    'command': WordCompleter(['USE', 'CREATE DATABASE']),
})
