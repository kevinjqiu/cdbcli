import functools
from prompt_toolkit.buffer import Buffer


open_file_in_editor = functools.partial(Buffer._open_file_in_editor, None)
