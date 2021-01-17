import argparse

from compiler import Compiler


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
    compiler = Compiler(args.input_file, args.output_file)
    compiler.read_from_file()
    compiler.compile()
    compiler.write_to_file()
