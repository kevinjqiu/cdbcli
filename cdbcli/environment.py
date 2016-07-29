import contextlib
import shlex
import subprocess
import sys


class Environment():
    def __init__(self, current_db=None, output_stream=sys.stdout):
        self.current_db = current_db
        self.output_stream = output_stream
        self.cli = None

    def output(self, text):
        if hasattr(self.output_stream, 'buffer'):
            buffer = self.output_stream.buffer
        else:
            buffer = self.output_stream

        buffer.write(bytes(text, encoding='utf-8'))
        buffer.write(bytes('\n', encoding='utf-8'))
        buffer.flush()

    def run_in_terminal(self, func, render_cli_done=False):
        assert self.cli, 'No CLI has been set'
        return self.cli.run_in_terminal(func, render_cli_done)

    @contextlib.contextmanager
    def pipe(self, shell_commands):
        prev_output_stream = self.output_stream

        subprocs = []
        for i, shell_command in enumerate(shell_commands):
            if i == len(shell_commands) -1:
                stdout = prev_output_stream
            else:
                stdout = subprocess.PIPE

            if i == 0:
                stdin = subprocess.PIPE
            else:
                stdin = subprocs[i - 1].stdin

            process = subprocess.Popen(shlex.split(shell_command),
                                    stdin=stdin,
                                    stdout=stdout)
            subprocs.append(process)

        if subprocs:
            self.output_stream = subprocs[0].stdin
        try:
            yield self
            if subprocs:
                subprocs[-1].communicate()
        finally:
            self.output_stream = prev_output_stream
