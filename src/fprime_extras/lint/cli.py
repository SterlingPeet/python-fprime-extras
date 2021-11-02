import argparse
import logging
import sys
from copy import copy
from pathlib import Path

import lxml.etree as etree
from lxml.etree import XMLSyntaxError

from ..core.conf import log_levels_dict as log_lvl
from ..core.file import ExtrasFile
from ..core.hooks import HookRegistry
from ..core.util import ConsoleLoggingContext as ConsoleLog
from .rules.base import LintSeverity
from .rules.registry import RuleListRegistry
from .xml import normalize

hooks = HookRegistry()
parser = argparse.ArgumentParser(
    description='The missing linter for F Prime projects.')


# TODO: build parser here if parser is not built already
# TODO: make help print the default values
def build_parser(parser):
    """Builds the parser for the linter cli.  Formulating this as a
    function allows this cli to be built either as a standalone callable
    or as a subcommand in a collection of callables.
    """
    # TODO: This is a hack?  want to display defaults and get them even
    #       if not specified, but not puke because they aren't specified
    #       type=argparse.FileType("r"),
    parser.add_argument('--config', nargs='?', type=argparse.FileType("r"),  # default='fplint.yml',
                        help='Configuration file for lint tuning')
    parser.add_argument('--normalize', action='store_true',
                        help='Reformat file only, without making other changes')
    parser.add_argument('--print-processing-instructions', action='store_true',
                        help='Print out the xml PIs discovered during parsing')
    parser.add_argument('--fix', action='store_true',
                        help="Try to fix the document and save the result")
    # This is the strategy to load rule-specific arguments
    hooks.define('fprime_extras/lint/config_args')
    hooks.define('fprime_extras/lint/file_type_check')
    hooks.define('fprime_extras/lint/raw_file_rules')
    hooks.define('fprime_extras/lint/document_model_rules')
    hooks.define('fprime_extras/lint/fprime_model_rules')
    for rule in RuleListRegistry().db:
        rule.register_hook_callbacks()
    for callback in hooks('fprime_extras/lint/config_args'):
        conf = callback()
        for key, vals in conf:
            parser.add_argument("--" + key, **vals)


def lint_main(args=None, parser=None):
    """Main linting program flow.

    The linter takes in command line arguments and configuration info,
    then checks for issues in the configured locations.

    TODO: policy for loading cli arguments for individual linting rules
    TODO: loading configuration from multiple files, e.g.: /etc, .config

    TODO: send useful information to log file
    TODO: send all human-consumed info to stderr
    TODO: send all machine-consumed (eclipse!) info to stdout

    The linter operates in stages, in order to collect as much info
    as possible before any early termination conditions might apply.
    These are the stages:

    TODO: dont forget xml tree hook and local/global model hooks

    1.  Find current target file for linting
    2.  Test that file is valid to lint, load file from disk
    3.  Determine what type of file (xml/cpp, topology/component) it is
    4.  Perform lint checks that run on a raw file
    5.  Load file into document model (e.g.: XML)
    6.  Perform checks that require a document model
    7.  Load F Prime model from document model
    8.  Perform checks that require a loaded F Prime model
    9.  Recursively load sub-models referenced by the F Prime target model
    10. Perform checks that require a fully loaded and referenced model
    11. Sort the collected output by file and line number
    12. Print the output in the requested format
    13. If Requested, normalize the file
    14. If Requested, fix the file? (this may be complicated)
    """
    if args is None and parser is not None:
        args = parser
    else:
        args = parser.parse_args(args=args)

    root_log = logging.getLogger('')
    console_handler = logging.StreamHandler(sys.stderr)
    root_log.addHandler(console_handler)
    root_log.setLevel(log_lvl[args.log_level])
    cli_log = logging.getLogger(__name__)

    lint_log = logging.getLogger('FP-LINT')

    if args.normalize:
        normalize(args.base_file)

    else:
        notifications = []
        crit_flag = False

        # STEP 0: Register rule callbacks

        # STEP 1: Find current target file for linting
        base_filepath = Path(args.base_file)

        # STEP 2: Test that file is valid to lint, load file from disk
        # STEP 3: Determine what filetype it is
        if base_filepath.suffix != '.xml':
            cli_log.critical(
                'The file type \'{}\' is not supported.'.format(base_filepath.suffix))
            exit(1)
            # TODO: Instead of checking the file here, catch an UnexpectedFileTypeError instead
        # TODO: Move this to the notification printing code
        cli_log.info('Loading file %s', args.base_file)
        base_file = ExtrasFile(base_filepath)

        # STEP 4: Perform lint checks that run on a raw file
        # FIXME: It will be a performance problem to parse the xml file
        #        twice, but maybe not as bad as loading from the disk
        #        twice?
        for rule in hooks('fprime_extras/lint/raw_file_rules'):
            notes = rule(copy(args), base_file)
            for note in notes:
                if note.severity is LintSeverity.CRITICAL:
                    crit_flag = True
            notifications = notifications + notes

        # 5.  Load file into document model (e.g.: XML)
        if not crit_flag:
            xml_tree = None
            try:
                # TODO: This is probably not necessary, as linting should be
                #       halted by now if the document won't parse correctly.
                xml_tree = etree.parse(base_file)
            except XMLSyntaxError as e:
                cli_log.critical('\r\nXML Parsing Error:')
                cli_log.critical(e)

        # 6.  Perform checks that require a document model
        if not crit_flag:
            for rule in hooks('fprime_extras/lint/document_model_rules'):
                notes = rule(copy(args), base_file, xml_tree)
                for note in notes:
                    if note.severity is LintSeverity.CRITICAL:
                        crit_flag = True
                notifications = notifications + notes

        # 7.  Load F Prime model from document model
        # TODO: write a model for representing the software

        # 8.  Perform checks that require a loaded F Prime model
        if not crit_flag:
            for rule in hooks('fprime_extras/lint/fprime_model_rules'):
                notes = rule(copy(args), base_file, xml_tree, None)
                for note in notes:
                    if note.severity is LintSeverity.CRITICAL:
                        crit_flag = True
                notifications = notifications + notes

        # 11. Sort the collected output by file and line number
        notifications.sort(key=lambda x: x.line_number)
        # 12. Print the output in the requested format
        console_handler = logging.StreamHandler(sys.stderr)
        # lint_log.addHandler(console_handler)
        # formatter = logging.Formatter(log_frmat)

        rv_list = []
        with ConsoleLog(lint_log):  # , handler=console_handler):
            lint_log.info('**************** %s', base_filepath)
            for item in notifications:
                note_list = []
                note_list.append('[FP-LINT] (L{},'.format(item.line_number))
                note_list.append('C{}) '.format(item.column))
                note_list.append('{} -> '.format(item.rule_slug))
                note_list.append('{} '.format(item.description))
                note_list.append('[{}]'.format(item.severity.name))
                lint_log.warning(''.join(note_list))
                rv_list.append(RuleViolationError(item.rule_slug,
                                                  item.line_number,
                                                  item.description))

            if len(notifications) == 0:
                lint_log.info('All linting checks passed.')

        if len(rv_list) > 0:
            # TODO: raise a lint error exception?
            sys.exit(-1)


            # if args.fix:
            #     top_tree.write(base_file, xml_declaration=True,
            #                    encoding='UTF-8', pretty_print=True)
