import argparse

from code_generator import CodeGenerator
from compiler_exception import CompilerException
from lexer import CompilerLexer
from parser import CompilerParser
from pre_parser import CompilerPreParser
from variable_prepare import VariablePrepare


def parse_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        'input_file',
        help='.imp file'
    )
    argument_parser.add_argument(
        'output_file',
        help='.mr file'
    )
    return argument_parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    with open(args.input_file, 'r') as input_file:
        code = input_file.read()
        lexer = CompilerLexer()
        pre_parser = CompilerPreParser()
        try:
            pre_parse_ready = lexer.tokenize(code)
            parse_ready = lexer.tokenize(code)
            variables = pre_parser.parse(pre_parse_ready)
            variable_prepare = VariablePrepare(variables)
            optimized_variables = variable_prepare.get_optimized_variables()
            variable_prepare.print_variables()
            generator = CodeGenerator(optimized_variables)
            parser = CompilerParser(generator)
            parser.parse(parse_ready)
            with open(args.output_file, 'w') as output_file:
                output_file.write("\n".join(generator.commands))
        except CompilerException as e:
            print("Error: {} on line {}".format(e.error, e.line))
