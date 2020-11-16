import lxml.etree as etree
from lxml.etree import XMLSyntaxError

from ..core.file import ExtrasFile


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
                            port_dict['kind'] = port.get(
                                key)[0:-6].capitalize()
                    if key == 'data_type':
                        port_dict['data_type'] = '[`{}`]()'.format(
                            port.get(key))
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
                        cmd_dict[key] = '{val} (0x{val:X})'.format(
                            val=int(command.get(key)))
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
                        chan_dict[key] = '{val} (0x{val:X})'.format(
                            val=int(channel.get(key)))
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
                        event_dict[key] = '{val} (0x{val:X})'.format(
                            val=int(event.get(key)))
                event_list.append(event_dict)
    return event_list, event_keys, event_titles


def parse_parameter_list(parameters_root):
    return []  # TODO
