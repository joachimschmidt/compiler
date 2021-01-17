from code_generator import CodeGenerator
from definitions.compiler_exception import CompilerException
from lexer import CompilerLexer
from parser import CompilerParser
from pre_parser import CompilerPreParser
from variable_prepare import VariablePrepare


class Compiler:
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out
        self.code = None
        self.commands = []
        self.variables = {}
        self.error = False

    def read_from_file(self):
        with open(self.file_in, 'r') as input_file:
            self.code = input_file.read()

    def compile(self):
        lexer = CompilerLexer()
        pre_parser = CompilerPreParser()
        try:
            pre_parse_ready = lexer.tokenize(self.code)
            parse_ready = lexer.tokenize(self.code)
            self.variables = pre_parser.parse(pre_parse_ready)
            variable_prepare = VariablePrepare(self.variables)
            optimized_variables = variable_prepare.get_optimized_variables()
            #variable_prepare.print_variables()
            generator = CodeGenerator(optimized_variables)
            parser = CompilerParser(generator)
            parser.parse(parse_ready)
            self.commands = generator.commands
        except CompilerException as e:
            self.error = True
            print("Error: {} on line {}".format(e.error, e.line))

    def write_to_file(self):
        if not self.error:
            with open(self.file_out, 'w') as output_file:
                output_file.write("\n".join(self.commands))
                return True
        else:
            return False
