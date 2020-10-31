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
        generate_component_documentation(args.base_file)
    elif ai_file_type == "TopologyApp":
        generate_topology_documentation(args.base_file, args.fprime_root)


def generate_topology_documentation(file_name, fprime_root):
    xml_file = ExtrasFile(file_name)
    xml_tree = None
    try:
        xml_tree = etree.parse(xml_file)
    except XMLSyntaxError as e:
        print('\r\nXML Parsing Error:')
        print(e)
        exit(-1)

    comp_root = xml_tree.getroot()
    if comp_root.tag != 'assembly':
        print('Topology assembly root not found!')
        exit(-1)

    imported_components = []
    for child in comp_root:
        if child.tag == 'import_component_type':
            component_file = "{}/{}".format(fprime_root, child.text)
            print("Found Component: {}".format(component_file))
            imported_components.append(component_file)

    # acquire component names and details
    component_names = []
    telemetry = []
    ports = []
    events = []
    commands = []
    for component in imported_components:
        port_list, command_list, telemetry_list, event_list, comp_root = parse_components_file(component)
        if comp_root.tag == "component" and "name" in comp_root.attrib.keys():
            component_name = comp_root.attrib["name"]
            component_names.append(component_name)
            telemetry.append(telemetry_list)
            ports.append(port_list)
            commands.append(command_list)
            events.append(event_list)

    # build docs file now
    print("\r\nHere is the summary of all components in this deployment")
    # Lets build the command list
    command_count = sum([len(command_list) for command_list in commands])
    if command_count > 0:
        _, cmd_keys, cmd_titles = parse_command_list(None)
        cmd_keys.append("Component")
        cmd_titles["Component"] = "Component Name"

        print('\r\n\r\n## Command List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + cmd_titles[t] + ' ' for t in cmd_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in cmd_keys]) + delimiter)
        for component_name, command_list in zip(component_names, commands):
            for cmd_dict in command_list:
                cmd_dict["Component"] = component_name
                print(delimiter + delimiter.join([' ' + cmd_dict[i] + ' ' for i in cmd_keys]) + delimiter)
    else:
        print('\r\n\r\n## Command List\r\n\r\nThis deployment has no commands.')

    # Lets build the telemetry list
    telemetry_count = sum([len(telemetry_list) for telemetry_list in telemetry])
    if telemetry_count > 0:
        _, channel_keys, channel_titles = parse_telemetry_list(None)
        channel_keys.append("Component")
        channel_titles["Component"] = "Component Name"

        print('\r\n## Telemetry Channel List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + channel_titles[t] + ' ' for t in channel_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in channel_keys]) + delimiter)
        for component_name, telemetry_list in zip(component_names, telemetry):
            for chan_dict in telemetry_list:
                chan_dict["Component"] = component_name
                print(delimiter + delimiter.join([' ' + chan_dict[i] + ' ' for i in channel_keys]) + delimiter)
    else:
        print('\r\n## Telemetry Channel List\r\n\r\nThis deployment has no telemetry.')

    # Lets build the event list
    event_count = sum([len(event_list) for event_list in events])
    if event_count > 0:
        _, event_keys, event_titles = parse_event_list(None)
        event_keys.append("Component")
        event_titles["Component"] = "Component Name"

        print('\r\n## Event List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + event_titles[t] + ' ' for t in event_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in event_keys]) + delimiter)
        for component_name, event_list in zip(component_names, events):
            for event_dict in event_list:
                event_dict["Component"] = component_name
                print(delimiter + delimiter.join([' ' + event_dict[i] + ' ' for i in event_keys]) + delimiter)
    else:
        print('\r\n## Event List\r\n\r\nThis deployment has no events.')

    print('\r\n\r\nPort Table for deployment')

    # Lets build the port list
    port_count = sum([len(port_list) for port_list in ports])
    if port_count > 0:
        _, port_keys, port_titles = parse_port_list(None)
        port_keys.append("Component")
        port_titles["Component"] = "Component Name"

        print('\r\n\r\n## Port List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + port_titles[p] + ' ' for p in port_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for p in port_keys]) + delimiter)
        for component_name, port_list in zip(component_names, ports):
            for port_dict in port_list:
                port_dict["Component"] = component_name
                print(delimiter + delimiter.join([' ' + port_dict[i] + ' ' for i in port_keys]) + delimiter)
    else:
        print('\r\n\r\n## Port List\r\n\r\nThis deployment has no commands.')
    print('\r\n')



def generate_component_documentation(file_name):
    port_list, command_list, telemetry_list, event_list, comp_root = parse_components_file(file_name)

    for child in comp_root:
        if child.tag == 'ports':
            print("Found ports")
        if child.tag == 'commands':
            print("Found commands")
        if child.tag == 'telemetry':
            print("Found telemetry")
        if child.tag == 'events':
            print("Found events")

    # OK, build the docs file now
    print('\r\nHere is the contents of the docs/{}.md file:'.format(comp_root.get('name')))
    # Lets build the command list
    if len(command_list) > 0:
        _, cmd_keys, cmd_titles = parse_command_list(None)

        print('\r\n\r\n## Command List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + cmd_titles[t] + ' ' for t in cmd_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in cmd_keys]) + delimiter)
        for cmd_dict in command_list:
            print(delimiter + delimiter.join([' ' + cmd_dict[i] + ' ' for i in cmd_keys]) + delimiter)
    else:
        print('\r\n\r\n## Command List\r\n\r\nThis component has no commands.')

    if len(telemetry_list) > 0:
        _, channel_keys, channel_titles = parse_telemetry_list(None)

        print('\r\n## Telemetry Channel List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + channel_titles[t] + ' ' for t in channel_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in channel_keys]) + delimiter)
        for chan_dict in telemetry_list:
            print(delimiter + delimiter.join([' ' + chan_dict[i] + ' ' for i in channel_keys]) + delimiter)
    else:
        print('\r\n## Telemetry Channel List\r\n\r\nThis component has no telemetry.')

    if len(event_list) > 0:
        _, event_keys, event_titles = parse_event_list(None)

        print('\r\n## Event List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + event_titles[t] + ' ' for t in event_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for t in event_keys]) + delimiter)
        for event_dict in event_list:
            print(delimiter + delimiter.join([' ' + event_dict[i] + ' ' for i in event_keys]) + delimiter)
    else:
        print('\r\n## Event List\r\n\r\nThis component has no events.')

    print('\r\n\r\nPort Table for docs/sdd.md:')

    # Lets build the command list
    if len(port_list) > 0:
        _, port_keys, port_titles = parse_port_list(None)

        print('\r\n\r\n## Port List\r\n')
        delimiter = '|'
        print(delimiter + delimiter.join([' ' + port_titles[p] + ' ' for p in port_keys]) + delimiter)
        print(delimiter + delimiter.join([' --- ' for p in port_keys]) + delimiter)
        for port_dict in port_list:
            print(delimiter + delimiter.join([' ' + port_dict[i] + ' ' for i in port_keys]) + delimiter)
    else:
        print('\r\n\r\n## Port List\r\n\r\nThis component has no commands.')
    print('\r\n')


def parse_components_file(file_name):
    xml_file = ExtrasFile(file_name)
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

    ports = None
    commands = None
    telemetry = None
    events = None
    for child in comp_root:
        if child.tag == 'ports':
            ports = child
        if child.tag == 'commands':
            commands = child
        if child.tag == 'telemetry':
            telemetry = child
        if child.tag == 'events':
            events = child
    ports_list, _, _ = parse_port_list(ports)
    commands_list, _, _ = parse_command_list(commands)
    telemetry_list, _, _ = parse_telemetry_list(telemetry)
    events_list, _, _ = parse_event_list(events)
    return ports_list, commands_list, telemetry_list, events_list, comp_root


def parse_port_list(ports_root):
    port_keys = ['data_type', 'name', 'direction', 'kind', 'comment']
    port_titles = {
        'data_type': 'Port Data Type',
        'name': 'Name',
        'direction': 'Direction',
        'kind': 'Kind',
        'comment': 'Usage',
    }
    port_list = []
    if ports_root is not None:
        for port in ports_root:
            port_dict = {}
            if port.tag == 'port':
                for key in port_keys:
                    port_dict[key] = port.get(key)
                    if port_dict[key] is None:
                        port_dict[key] = ' '
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
    return port_list, port_keys, port_titles


def parse_command_list(commands_root):
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
    if commands_root is not None:
        for command in commands_root:
            cmd_dict = {}
            if command.tag == 'command':
                for key in cmd_keys:
                    cmd_dict[key] = command.get(key)
                    if cmd_dict[key] is None:
                        cmd_dict[key] = ' '
                        for child in command:
                            if child.tag == key:
                                cmd_dict[key] = child.text.strip()
                    if key == 'opcode':
                        cmd_dict[key] = '{val} (0x{val:X})'.format(val=int(command.get(key)))
                cmd_list.append(cmd_dict)
    return cmd_list, cmd_keys, cmd_titles


def parse_telemetry_list(telemetry_root):
    channel_keys = ['name', 'id', 'data_type', 'comment']
    channel_titles = {
        'name': 'Channel',
        'id': 'ID',
        'data_type': 'Type',
        'comment': 'Description'
    }
    channel_list = []
    if telemetry_root is not None:
        for channel in telemetry_root:
            chan_dict = {}
            if channel.tag == 'channel':
                for key in channel_keys:
                    chan_dict[key] = channel.get(key)
                    if chan_dict[key] is None:
                        chan_dict[key] = ' '
                        for child in channel:
                            if child.tag == key:
                                chan_dict[key] = child.text.strip()
                    if key == 'id':
                        chan_dict[key] = '{val} (0x{val:X})'.format(val=int(channel.get(key)))
                channel_list.append(chan_dict)
    return channel_list, channel_keys, channel_titles


def parse_event_list(events_root):
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
    if events_root is not None:
        for event in events_root:
            event_dict = {}
            if event.tag == 'event':
                for key in event_keys:
                    event_dict[key] = event.get(key)
                    if event_dict[key] is None:
                        event_dict[key] = ' '
                        for child in event:
                            if child.tag == key:
                                event_dict[key] = child.text.strip()
                    if key == 'id':
                        event_dict[key] = '{val} (0x{val:X})'.format(val = int(event.get(key)))
                event_list.append(event_dict)
    return event_list, event_keys, event_titles


def parse_parameter_list(parameters_root):
    return []  # TODO
