import pygments
from pygments import lexers, formatters


def json(formatted_json):
    return pygments.highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())


def javascript(code):
    return pygments.highlight(code, lexers.JavascriptLexer(), formatters.TerminalFormatter())


def python(code):
    return pygments.highlight(code, lexers.PythonLexer(), formatters.TerminalFormatter())


def erlang(code):
    return pygments.highlight(code, lexers.ErlangLexer(), formatters.TerminalFormatter())
