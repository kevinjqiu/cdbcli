from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.layout.lexers import SimpleLexer
from prompt_toolkit.token import Token

from .grammar import grammar


lexer = GrammarLexer(grammar, lexers={
    'command': SimpleLexer(Token.Command),
    'operand': SimpleLexer(Token.Operand),
    'database_name': SimpleLexer(Token.Operand),
})
