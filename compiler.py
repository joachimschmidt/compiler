import argparse

from lexer import CompilerLexer
from parser import CompilerParser


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
        parser = CompilerParser()
        try:
            parse_ready = lexer.tokenize(code)
            parser.parse(parse_ready)
        except Exception as e:
            print(e)
        commands = []

    with open(args.output_file, 'w') as output_file:
        output_file.write("\n".join(commands))
