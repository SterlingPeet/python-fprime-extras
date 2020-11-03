import argparse
from os.path import splitext

from ..docs import generate


parser = argparse.ArgumentParser(description='The missing docs generator for F Prime projects.')

def build_parser(parser):
    """Builds the parser for the docs cli.  Formulating this as a
    function allows this cli to be built either as a standalone callable
    or as a subcommand in a collection of callables.
    """
    parser.add_argument('base_file', metavar='FILE',
                        help='File to use for docs source')
    parser.add_argument('fprime_root', type=str, nargs='?',
                         help='FPrime root directory for topology parsing')
    parser.add_argument('-o', '--output',
                        help='Documentation file to generate')
    # TODO: add argument for fprime root location, for topology parsing

def docs_main(args=None, parser=None):
    if args is None and parser is not None:
        args = parser
    else:
        args = parser.parse_args(args=args)

    invalid_flag = False
    filename, file_extension = splitext(args.base_file)
    ai_file_type = None
    if file_extension != '.xml':
        print('This version only works with XML input files.')
        invalid_flag = True
    if filename[-2:] != 'Ai':
        print('Autocoder input files must have the suffix "Ai".')
        invalid_flag = True
    elif filename[-11:-2] == "Component":
        ai_file_type = "Component"
    elif filename[-13:-2] == "TopologyApp":
        ai_file_type = "TopologyApp"
        if args.fprime_root is None:
            print("Topology parsing requires fprime root directory argument")
            invalid_flag = True
    else:
        print(filename)
        print('This version can only handle Components.')
        invalid_flag = True

    if invalid_flag:
        exit(-1)


    print('Loading file {}'.format(args.base_file))
    # Ignore the rest of this file, its a hack, and probably needs
    # to be removed since it was written to auto-code files that are
    # actively being removed from F Prime.
    print(ai_file_type)
    if ai_file_type == "Component":
        generate.generate_component_documentation(args.base_file)
    elif ai_file_type == "TopologyApp":
        generate.generate_topology_documentation(args.base_file, args.fprime_root)
