import shlex

from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.layout.lexers import SimpleLexer
from prompt_toolkit.token import Token

from .grammar import grammar


lexer = GrammarLexer(grammar, lexers={
    'command': SimpleLexer(Token.Command),
    'operand': SimpleLexer(Token.Operand),
    'database_name': SimpleLexer(Token.Operand),
})


def split_cli_command_and_shell_commands(command_text):
    """Split the command text into cli commands and pipes

    e.g.::

        cat ID | grep text

    ``cat ID`` is a CLI command, which will be matched against the CLI grammar tree
    ``grep text`` is treated as a SHELL command

    Returns a tuple ``(a, b)`` where ``a`` is the CLI command, and ``b`` is a list of shell commands
    """
    tokens = shlex.split(command_text)
    parts = []
    stack = []
    for token in tokens:
        if token != '|':
            stack.append(token)
        else:
            parts.append(stack)
            stack = []

    if stack:
        parts.append(stack)

    if len(parts) == 1:
        return ' '.join(parts[0]), []

    return ' '.join(parts[0]), parts[1:]
