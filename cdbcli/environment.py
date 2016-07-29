import sys
import contextlib


class Environment():
    def __init__(self, current_db=None, output_stream=sys.stdout):
        self.current_db = current_db
        self.output_stream = output_stream
        self.cli = None
        self.pipes = []

    def output(self, text):
        self.output_stream.write(text)
        self.output_stream.write('\n')
        self.output_stream.flush()

    def run_in_terminal(self, func, render_cli_done=False):
        assert self.cli, 'No CLI has been set'
        return self.cli.run_in_terminal(func, render_cli_done)

    @contextlib.contextmanager
    def handle_pipes(self, pipes):
        self.pipes = pipes

        subprocesses = []
        for shell_command in pipes:
            subprocesses.append(subprocess.run(shlex.split(shell_command),
                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE))

        try:
            yield self
        finally:
            self.pipes = []
