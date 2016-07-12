from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar


completer = GrammarCompleter(grammar, {
})
