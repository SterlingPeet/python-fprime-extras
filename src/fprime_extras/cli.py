"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mfprime_extras` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``fprime_extras.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``fprime_extras.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import textwrap

from . import __date__
from . import __version__
from . import __branch__
from .devupdate import nag, version_cache_file
from .docs.cli import build_parser as build_docs_parser
from .docs.cli import docs_main
from .lint.cli import build_parser as build_lint_parser
from .lint.cli import lint_main


def build_common_parser(parser):
    """Set the common options for all callable cli entry points in
    fprime_extras.
    """
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Print more output given more "v"')
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {version}, ({date})'.format(version=__version__,
                                                      date=__date__))
    parser.add_argument('--print-cache-file', action='store_true',
                        help='Print the path and name of the dev cache file')
    parser.add_argument('--print-cache-file-contents', action='store_true',
                        help='Print the contents of the version cache file')


parser = argparse.ArgumentParser(
    description=textwrap.dedent('''\
    %(prog)s : The missing F Prime development tool set.
    Version {}'''.format(__version__)),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
    Written by Sterling Peet <sterling.peet@ae.gatech.edu>
    Space Systems Design Lab
    School of Aerospace Engineering
    Georgia Institute of Technology
    Atlanta, GA, USA'''))
build_common_parser(parser)
subparsers = parser.add_subparsers(title='Extras Command List')
docs_parser = subparsers.add_parser(
    'docs', help='Documentation file template generator and updater')
impl_parser = subparsers.add_parser(
    'impl', help='Implementation file template generator and updater')
lint_parser = subparsers.add_parser(
    'lint', help='Lint checker for F Prime format and structure')
build_docs_parser(docs_parser)
docs_parser.set_defaults(func=docs_main)
build_lint_parser(lint_parser)
lint_parser.set_defaults(func=lint_main)


def main(args=None):
    args = parser.parse_args(args=args)

    if args.print_cache_file:
        print('Version Check Cache File: {}'.format(version_cache_file))

    if args.print_cache_file_contents:
        print('Version Check Cache File Contents:')
        with open(version_cache_file, 'r') as f:
            print(f.read())

    if hasattr(args, 'func'):
        args.func(parser=args)
    else:
        print('No Sub-command was invoked, doing nothing.')

    try:
        nag(__version__, __branch__)
    except Exception as e:
        if args.verbose > 0:
            raise e
