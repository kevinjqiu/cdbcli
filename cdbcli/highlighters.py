import json as simplejson
import pygments
from pygments import lexers, formatters


def json(json_object):
    formatted_json = simplejson.dumps(json_object, sort_keys=True, indent=4)
    return pygments.highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())


def javascript(code):
    return pygments.highlight(code, lexers.JavascriptLexer(), formatters.TerminalFormatter())


def python(code):
    return pygments.highlight(code, lexers.PythonLexer(), formatters.TerminalFormatter())
