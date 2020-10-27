import argparse
from os.path import splitext

import lxml.etree as etree
from lxml.etree import XMLSyntaxError

from ..core.file import ExtrasFile


parser = argparse.ArgumentParser(description='The missing docs generator for F Prime projects.')

def build_parser(parser):
    """Builds the parser for the docs cli.  Formulating this as a
    function allows this cli to be built either as a standalone callable
    or as a subcommand in a collection of callables.
    """
    parser.add_argument('base_file', metavar='FILE',
                        help='File to use for docs source')
    parser.add_argument('-o', '--output',
                        help='Documentation file to generate')


def docs_main(args=None, parser=None):
    if args is None and parser is not None:
        args = parser
    else:
        args = parser.parse_args(args=args)

    invalid_flag = False
    filename, file_extension = splitext(args.base_file)
    if file_extension != '.xml':
        print('This version only works with XML input files.')
        invalid_flag = True
    if filename[-2:] != 'Ai':
        print('Autocoder input files must have the suffix "Ai".')
        invalid_flag = True
    elif filename[-11:-2] != 'Component':
        print(filename[-11:-2])
        print('This version can only handle Components.')
        invalid_flag = True

    if invalid_flag:
        exit(-1)


    print('Loading file {}'.format(args.base_file))
    xml_file = ExtrasFile(args.base_file)
    xml_tree = None
    try:
        xml_tree = etree.parse(xml_file)
    except XMLSyntaxError as e:
        print('\r\nXML Parsing Error:')
        print(e)
        exit(-1)

    comp_root = xml_tree.getroot()
    if comp_root.tag != 'component':
        print('Component model root not found!')
        exit(-1)

    # Ignore the rest of this file, its a hack, and probably needs
    # to be removed since it was written to auto-code files that are
    # actively being removed from F Prime.

    ports = None
    commands = None
    telemetry = None
    events = None
    for child in comp_root:
        if child.tag == 'ports':
            print("Found ports")
            ports = child
        if child.tag == 'commands':
            print("Found commands")
            commands = child
        if child.tag == 'telemetry':
            print("Found telemetry")
            telemetry = child
        if child.tag == 'events':
            print("Found events")
            events = child

    # OK, build the docs file now
    print('\r\nHere is the contents of the docs/{}.md file:'.format(comp_root.get('name')))
    # Lets build the command list
    if commands is not None:
        cmd_keys = ['mnemonic', 'opcode', 'comment', 'arg', 'type', 'comment2']
        cmd_titles = {
                        'mnemonic': 'Mnemonic',
                        'comment': 'Description',
                        'opcode': 'ID',
                        'arg': 'Arg Name',
                        'type': 'Arg Type',
                        'comment2': 'Comment'
        }
        cmd_list = []
        for command in commands:
            cmd_dict = {}
            if command.tag == 'command':
                for key in cmd_keys:
                    cmd_dict[key] = command.get(key)
                    if cmd_dict[key] is None:
                        for child in command:
                            if child.tag == key:
                                cmd_dict[key] = child.text.strip()
                    if key == 'opcode':
                        cmd_dict[key] = '{val} (0x{val:X})'.format(val = int(command.get(key)))
                cmd_list.append(cmd_dict)

        print('\r\n\r\n## Command List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' '+cmd_titles[t]+' ' for t in cmd_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in cmd_keys]) + delimiter)
        for cmd_dict in cmd_list:
            for key in cmd_dict.keys():
                if cmd_dict[key] is None:
                    cmd_dict[key] = ' '
            print(delimiter + delimiter.join([' '+cmd_dict[i]+' ' for i in cmd_keys]) + delimiter)
    else:
        print('\r\n\r\n## Command List\r\n\r\nThis component has no commands.')

    if telemetry is not None:
        channel_keys = ['name', 'id', 'data_type', 'comment']
        channel_titles = {
                            'name': 'Channel',
                            'id': 'ID',
                            'data_type': 'Type',
                            'comment': 'Description'
        }
        channel_list = []
        for channel in telemetry:
            chan_dict = {}
            if channel.tag == 'channel':
                for key in channel_keys:
                    chan_dict[key] = channel.get(key)
                    if chan_dict[key] is None:
                        for child in channel:
                            if child.tag == key:
                                chan_dict[key] = child.text.strip()
                    if key == 'id':
                        chan_dict[key] = '{val} (0x{val:X})'.format(val = int(channel.get(key)))
                channel_list.append(chan_dict)

        print('\r\n## Telemetry Channel List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' '+channel_titles[t]+' ' for t in channel_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in channel_keys]) + delimiter)
        for chan_dict in channel_list:
            for key in chan_dict.keys():
                if chan_dict[key] is None:
                    chan_dict[key] = ' '
            print(delimiter + delimiter.join([' '+chan_dict[i]+' ' for i in channel_keys]) + delimiter)
    else:
        print('\r\n## Telemetry Channel List\r\n\r\nThis component has no telemetry.')

    if events is not None:
        event_keys = ['name', 'id', 'comment', 'arg', 'type', 'size', 'comment2']
        event_titles = {
                        'name': 'Event Name',
                        'comment': 'Description',
                        'id': 'ID',
                        'arg': 'Arg Name',
                        'type': 'Arg Type',
                        'size': 'Arg Size',
                        'comment2': 'Comment'
        }
        event_list = []
        for event in events:
            event_dict = {}
            if event.tag == 'event':
                for key in event_keys:
                    event_dict[key] = event.get(key)
                    if event_dict[key] is None:
                        for child in event:
                            if child.tag == key:
                                event_dict[key] = child.text.strip()
                    if key == 'id':
                        event_dict[key] = '{val} (0x{val:X})'.format(val = int(event.get(key)))
                event_list.append(event_dict)

        print('\r\n## Event List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' '+event_titles[t]+' ' for t in event_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in event_keys]) + delimiter)
        for event_dict in event_list:
            for key in event_dict.keys():
                if event_dict[key] is None:
                    event_dict[key] = ' '
            print(delimiter + delimiter.join([' '+event_dict[i]+' ' for i in event_keys]) + delimiter)
    else:
        print('\r\n## Event List\r\n\r\nThis component has no events.')

    print('\r\n\r\nPort Table for docs/sdd.md:')

    # Lets build the command list
    if ports is not None:
        port_keys = ['data_type', 'name', 'direction', 'kind', 'comment']
        port_titles = {
                        'data_type': 'Port Data Type',
                        'name': 'Name',
                        'direction': 'Direction',
                        'kind': 'Kind',
                        'comment': 'Usage',
        }
        port_list = []
        for port in ports:
            port_dict = {}
            if port.tag == 'port':
                for key in port_keys:
                    port_dict[key] = port.get(key)
                    if port_dict[key] is None:
                        for child in port:
                            if child.tag == key:
                                port_dict[key] = child.text.strip()
                    if key == 'kind':
                        if port.get(key)[-4] == 't':
                            port_dict['direction'] = 'Output'
                            port_dict['kind'] = 'Output'
                        else:
                            port_dict['direction'] = 'Input'
                            port_dict['kind'] = port.get(key)[0:-6].capitalize()
                    if key == 'data_type':
                        port_dict['data_type'] = '[`{}`]()'.format(port.get(key))
                port_list.append(port_dict)

        print('\r\n\r\n## Port List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' '+port_titles[p]+' ' for p in port_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for p in port_keys]) + delimiter)
        for port_dict in port_list:
            for key in port_dict.keys():
                if port_dict[key] is None:
                    port_dict[key] = ' '
            print(delimiter + delimiter.join([' '+port_dict[i]+' ' for i in port_keys]) + delimiter)
    else:
        print('\r\n\r\n## Port List\r\n\r\nThis component has no commands.')
    print('\r\n')
