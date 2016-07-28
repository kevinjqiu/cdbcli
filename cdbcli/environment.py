import sys


class Environment(object):
    def __init__(self, current_db=None, output_stream=sys.stdout):
        self.current_db = current_db
        self.output_stream = output_stream
        self.cli = None
        self.previous_db = None

    def output(self, text):
        self.output_stream.write(text)
        self.output_stream.write('\n')
        self.output_stream.flush()

    def run_in_terminal(self, func, render_cli_done=False):
        if not self.cli:
            raise RuntimeError('No cli has been set')

        return self.cli.run_in_terminal(func, render_cli_done)
