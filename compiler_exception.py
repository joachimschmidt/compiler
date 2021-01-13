class CompilerException(Exception):
    def __init__(self, error, line):
        self.error = error
        self.line = line
