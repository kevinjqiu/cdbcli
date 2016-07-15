import sys


class Environment(object):
    def __init__(self, current_db=None):
        self.current_db = current_db
        self.output_stream = sys.stdout

    def output(self, text):
        self.output_stream.write(text)
        self.output_stream.write('\n')
        self.output_stream.flush()
