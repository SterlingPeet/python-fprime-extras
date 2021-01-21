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
import logging
import sys
import textwrap
from logging.handlers import TimedRotatingFileHandler

from . import __branch__
from . import __date__
from . import __version__
from .core.conf import log_file
from .core.conf import log_file_format_str as log_frmat
from .core.conf import log_levels
from .core.util import ConsoleLoggingContext as ConsoleLog
from .devupdate import nag
from .devupdate import version_cache_file
from .docs.cli import build_parser as build_docs_parser
from .docs.cli import docs_main
from .lint.cli import build_parser as build_lint_parser
from .lint.cli import lint_main

log = logging.getLogger(__name__)


def build_base_parser(parser):
    """Set the options for the main command, not needed by sub
    commands.
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


def build_common_parser(parser):
    """Set the common options for all callable cli entry points in
    fprime_extras.
    """
    parser.add_argument('base_file', metavar='FILE',
                        help='File to operate upon')
    parser.add_argument('fprime_root', metavar='FPRIME_ROOT', type=str, nargs='?',
                        help='FPrime root directory for dependency parsing')
    parser.add_argument('--log-level', default='WARNING', choices=log_levels,
                        help='log file verbosity level')


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
build_base_parser(parser)
subparsers = parser.add_subparsers(title='Extras Command List')
docs_parser = subparsers.add_parser(
    'docs', help='Documentation file template generator and updater')
# impl_parser = subparsers.add_parser(
#     'impl', help='Implementation file template generator and updater')
lint_parser = subparsers.add_parser(
    'lint', help='Lint checker for F Prime format and structure')
build_common_parser(docs_parser)
build_docs_parser(docs_parser)
docs_parser.set_defaults(func=docs_main)
build_common_parser(lint_parser)
build_lint_parser(lint_parser)
lint_parser.set_defaults(func=lint_main)


def main(args=None):
    args = parser.parse_args(args=args)

    console_handler = logging.StreamHandler(sys.stderr)
    log.addHandler(console_handler)
    formatter = logging.Formatter(log_frmat, datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=10)
    file_handler.setFormatter(formatter)
    root_log = logging.getLogger('')
    root_log.addHandler(file_handler)

    with ConsoleLog(log, handler=console_handler):
        if args.print_cache_file:
            log.info('Version Check Cache File: {}'.format(version_cache_file))

        if args.print_cache_file_contents:
            log.info('Version Check Cache File Contents:')
            with open(version_cache_file, 'r') as f:
                log.info(f.read())

    if hasattr(args, 'func'):
        args.func(parser=args)
    else:
        log.warning('No Sub-command was invoked, doing nothing.')

    try:
        nag(__version__, __branch__)
    except Exception as e:
        if args.verbose > 0:
            log.error('\nPrinting Traceback due to requested verbosity:\n')
            raise e
