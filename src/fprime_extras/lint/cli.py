import argparse
import lxml.etree as etree
from lxml.etree import DocumentInvalid
from lxml.etree import XMLSyntaxError
from lxml.isoschematron import Schematron
from os.path import splitext
import os

from .xml import normalize
from ..core.file import ExtrasFile
from .rules import RuleListFactory

parser = argparse.ArgumentParser(description='The missing linter for F Prime projects.')

def build_parser(parser):
    """Builds the parser for the linter cli.  Formulating this as a
    function allows this cli to be built either as a standalone callable
    or as a subcommand in a collection of callables.
    """
    parser.add_argument('base_file', metavar='FILE',
                        help='File to lint')
    parser.add_argument('--normalize', action='store_true',
                        help='Reformat file only, without making other changes')
    parser.add_argument('--print-processing-instructions', action='store_true',
                        help='Print out the xml PIs discovered during parsing')
    parser.add_argument('--fix', action='store_true',
                        help="Try to fix the document and save the result")


def lint_main(args=None, parser=None):
    if args is None and parser is not None:
        args = parser
    else:
        args = parser.parse_args(args=args)

    all_rules = RuleListFactory().rules()
    print("Rules collected: {}".format(len(all_rules)))

    if args.normalize:
        normalize(args.base_file)

    else:
        filename, file_extension = splitext(args.base_file)
        if file_extension == '.xml':
            print('Loading file {}'.format(args.base_file))
            xml_file = ExtrasFile(args.base_file)
            xml_tree = None
            try:
                xml_tree = etree.parse(xml_file)
            except XMLSyntaxError as e:
                print('\r\nXML Parsing Error:')
                print(e)
                exit(-1)

            # Try to validate against RNG schema
            pi_list = xml_tree.xpath('//processing-instruction()')
            schema_pi = None
            for pi in pi_list:
                if args.print_processing_instructions:
                    print(pi)
                if pi.target == 'xml-model':
                    schema_pi = pi
                if pi.target == 'oxygen':
                    try:
                        if pi.get('RNGSchema'):
                            print('** WARNING: Outdated Schema definition style!')
                            schema_pi = pi
                    except:
                        pass

            rng_filename = None
            rng_exists = False
            if schema_pi is None:
                print('** WARNING: No Schema PI detected!')
            elif schema_pi.target == 'xml-model':
                print('RNG Schema type: {}'.format(schema_pi.get('type')))
                print('RNG Namespace: {}'.format(schema_pi.get('schematypens')))
                print('RNG Validation File: {}'.format(schema_pi.get('href')))
                rng_filename = xml_file.resolve_relative_path(schema_pi.get('href'))
                print('RNG File Resolved: {}'.format(rng_filename))
                if os.path.exists(rng_filename):
                    print('File Exists!')
                    rng_exists = True
                else:
                    print('Path is invalid...')
            elif schema_pi.target == 'oxygen':
                print('RNG Schema type: {}'.format(schema_pi.get('type')))
                print('RNG Validation File: {}'.format(schema_pi.get('RNGSchema')))
                rng_filename = xml_file.resolve_relative_path(schema_pi.get('RNGSchema')[5:])
                print('RNG File Resolved: {}'.format(rng_filename))
                if os.path.exists(rng_filename):
                    print('File Exists!')
                    rng_exists = True
                else:
                    print('Path is invalid...')

            if rng_exists:
                print('Validating file against provided schema.')
                relaxng = etree.RelaxNG(file=rng_filename)
                try:
                    relaxng.assertValid(xml_tree)
                except DocumentInvalid:
                    print('\r\n*** An RNG Schema validation error has occured: \r\n')
                    log = relaxng.error_log
                    print(log)
                # try:
                #     schematron = Schematron(file='../../Autocoders//Python/schema/default/channel_id_schematron.rng')
                #     schematron.assertValid(xml_tree)
                #     print('Validation complete.')
                # except DocumentInvalid as e:
                #     # print(e)
                #     print('\r\n*** A Schematron validation error has occured: \r\n')
                #     log = schematron.error_log
                #     print(log)


            if xml_tree.getroot().tag == 'assembly':
                print('This is a topology file.')

                top_tree = xml_tree
                top_root = top_tree.getroot()

                print("Inspecting file {}".format(args.base_file))
                # print(xml_file.readline())
                # print(xml_file.readline())

                if top_root.tag != 'assembly':
                    print('Input file is not a topology xml file.')
                    exit(1)

                # Make lists of tags
                tag_lists_dict = {}
                for child in top_root:
                    if not child.tag in tag_lists_dict:
                        tag_lists_dict[child.tag] = []
                    tag_lists_dict[child.tag].append(child)

                for key in tag_lists_dict:
                    print('Found {} {} elements.'.format(len(tag_lists_dict[key]), key))

                # Pre-compute list of instance names for checking against
                instance_names = [i.get('name') for i in tag_lists_dict['instance']]
                print('\nFinding connections.')
                for conn in tag_lists_dict['connection']:
                    conn_name = conn.get('name')
                    source = ''
                    target = ''
                    flag = False
                    for comp in conn:
                        if comp.tag == 'source':
                            source = comp.get('component')
                        if comp.tag == 'target':
                            target = comp.get('component')
                    # print('Found connection "{}" from "{}" to "{}"'.format(conn_name, source, target))
                    if source not in instance_names:
                        print('Connection "{}"" contains non-existent source "{}"'.format(conn_name, source))
                        flag = True

                    if target not in instance_names:
                        print('Connection "{}"" contains non-existent target "{}"'.format(conn_name, target))
                        flag = True

                    if args.fix and flag:
                        conn.getparent().remove(conn)

                if args.fix:
                    # TODO: Save backup, also fix pretty-print problems
                    top_tree.write(xml_file, xml_declaration=True, encoding='UTF-8', pretty_print=True)

        else:
            print('The file type \'{}\' is not supported.'.format(file_extension))
            exit(-1)
