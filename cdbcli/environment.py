import contextlib
import io
import subprocess
import sys


class Environment():
    def __init__(self, current_db=None, output_stream=sys.stdout):
        self.current_db = current_db
        self.output_stream = output_stream
        self.cli = None
        self.previous_db = None
        self.has_pipe = False

    def output(self, text, highlighter=None):
        """Send text to the environment's output stream.
        :param text: the text to output
        :param highlighter: an optional function to colourize the text
        """
        if not self.has_pipe:  # only colourize when the output is not piped
            highlighter = highlighter or (lambda x: x)
            text = highlighter(text)
        output = "{}\n".format(text)
        if isinstance(self.output_stream, io.BufferedIOBase):
            output = bytes(output, encoding='utf-8')

        self.output_stream.write(output)
        self.output_stream.flush()

    def run_in_terminal(self, func, render_cli_done=False):
        assert self.cli, 'No CLI has been set'
        return self.cli.run_in_terminal(func, render_cli_done)

    @classmethod
    def _create_piped_subprocs(cls, shell_commands, final_stdout):
        subprocs = []
        for i, shell_command in enumerate(shell_commands):
            if i == len(shell_commands) - 1:
                stdout = final_stdout
            else:
                stdout = subprocess.PIPE

            if i == 0:
                stdin = subprocess.PIPE
            else:
                stdin = subprocs[i - 1].stdout

            try:
                process = subprocess.Popen(shell_command, stdin=stdin, stdout=stdout, stderr=sys.stderr)
            except OSError as e:
                raise RuntimeError(str(e))
            else:
                subprocs.append(process)

        return subprocs

    @contextlib.contextmanager
    def pipe(self, shell_commands):
        prev_output_stream = self.output_stream

        try:
            subprocs = self._create_piped_subprocs(shell_commands, prev_output_stream)
            if subprocs:
                self.has_pipe = True
                self.output_stream = subprocs[0].stdin

            yield self
            if subprocs:
                subprocs[0].communicate()
        finally:
            self.output_stream = prev_output_stream
            self.has_pipe = False
