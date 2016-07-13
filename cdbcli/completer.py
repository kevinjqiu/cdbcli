from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from .grammar import grammar
from .commands import COMMANDS


completer = GrammarCompleter(grammar, {
    'command': WordCompleter(COMMANDS.keys()),
})
