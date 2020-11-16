import lxml.etree as etree
from lxml.etree import XMLSyntaxError
from ..core.file import ExtrasFile
from ..docs.parse import parse_port_list, parse_event_list, parse_telemetry_list,\
    parse_command_list, parse_components_file


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
        port_list, command_list, telemetry_list, event_list, comp_root = parse_components_file(
            component)
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
        print(
            delimiter + delimiter.join([' ' + cmd_titles[t] + ' ' for t in cmd_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in cmd_keys]) + delimiter)
        for component_name, command_list in zip(component_names, commands):
            for cmd_dict in command_list:
                cmd_dict["Component"] = component_name
                print(
                    delimiter + delimiter.join([' ' + cmd_dict[i] + ' ' for i in cmd_keys]) + delimiter)
    else:
        print('\r\n\r\n## Command List\r\n\r\nThis deployment has no commands.')

    # Lets build the telemetry list
    telemetry_count = sum([len(telemetry_list)
                           for telemetry_list in telemetry])
    if telemetry_count > 0:
        _, channel_keys, channel_titles = parse_telemetry_list(None)
        channel_keys.append("Component")
        channel_titles["Component"] = "Component Name"

        print('\r\n## Telemetry Channel List\r\n')
        delimiter = '|'
        print(
            delimiter + delimiter.join([' ' + channel_titles[t] + ' ' for t in channel_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in channel_keys]) + delimiter)
        for component_name, telemetry_list in zip(component_names, telemetry):
            for chan_dict in telemetry_list:
                chan_dict["Component"] = component_name
                print(
                    delimiter + delimiter.join([' ' + chan_dict[i] + ' ' for i in channel_keys]) + delimiter)
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
        print(
            delimiter + delimiter.join([' ' + event_titles[t] + ' ' for t in event_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in event_keys]) + delimiter)
        for component_name, event_list in zip(component_names, events):
            for event_dict in event_list:
                event_dict["Component"] = component_name
                print(
                    delimiter + delimiter.join([' ' + event_dict[i] + ' ' for i in event_keys]) + delimiter)
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
        print(
            delimiter + delimiter.join([' ' + port_titles[p] + ' ' for p in port_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for p in port_keys]) + delimiter)
        for component_name, port_list in zip(component_names, ports):
            for port_dict in port_list:
                port_dict["Component"] = component_name
                print(
                    delimiter + delimiter.join([' ' + port_dict[i] + ' ' for i in port_keys]) + delimiter)
    else:
        print('\r\n\r\n## Port List\r\n\r\nThis deployment has no commands.')
    print('\r\n')


def generate_component_documentation(file_name):
    port_list, command_list, telemetry_list, event_list, comp_root = parse_components_file(
        file_name)

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
        print(
            delimiter + delimiter.join([' ' + cmd_titles[t] + ' ' for t in cmd_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in cmd_keys]) + delimiter)
        for cmd_dict in command_list:
            print(
                delimiter + delimiter.join([' ' + cmd_dict[i] + ' ' for i in cmd_keys]) + delimiter)
    else:
        print('\r\n\r\n## Command List\r\n\r\nThis component has no commands.')

    if len(telemetry_list) > 0:
        _, channel_keys, channel_titles = parse_telemetry_list(None)

        print('\r\n## Telemetry Channel List\r\n')
        delimiter = '|'
        print(
            delimiter + delimiter.join([' ' + channel_titles[t] + ' ' for t in channel_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in channel_keys]) + delimiter)
        for chan_dict in telemetry_list:
            print(
                delimiter + delimiter.join([' ' + chan_dict[i] + ' ' for i in channel_keys]) + delimiter)
    else:
        print('\r\n## Telemetry Channel List\r\n\r\nThis component has no telemetry.')

    if len(event_list) > 0:
        _, event_keys, event_titles = parse_event_list(None)

        print('\r\n## Event List\r\n')
        delimiter = '|'
        print(
            delimiter + delimiter.join([' ' + event_titles[t] + ' ' for t in event_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for t in event_keys]) + delimiter)
        for event_dict in event_list:
            print(
                delimiter + delimiter.join([' ' + event_dict[i] + ' ' for i in event_keys]) + delimiter)
    else:
        print('\r\n## Event List\r\n\r\nThis component has no events.')

    print('\r\n\r\nPort Table for docs/sdd.md:')

    # Lets build the command list
    if len(port_list) > 0:
        _, port_keys, port_titles = parse_port_list(None)

        print('\r\n\r\n## Port List\r\n')
        delimiter = '|'
        print(
            delimiter + delimiter.join([' ' + port_titles[p] + ' ' for p in port_keys]) + delimiter)
        print(delimiter +
              delimiter.join([' --- ' for p in port_keys]) + delimiter)
        for port_dict in port_list:
            print(
                delimiter + delimiter.join([' ' + port_dict[i] + ' ' for i in port_keys]) + delimiter)
    else:
        print('\r\n\r\n## Port List\r\n\r\nThis component has no commands.')
    print('\r\n')
