import subprocess
import sys
import xml.etree.ElementTree as ET

instance_tag = "instance"
connection_tag = "connection"
source_tag = "source"
target_tag = "target"
port_tag = "port"
component_tag = "component"
name_tag = "name"

port_ID = 1
cluster_ID = 1

# tutorial at: https://docs.python.org/3/library/xml.etree.elementtree.html


def find_unique_port_ID(component_name, port_name, component_port_mapping):
    """
    returns the ID of the port, or -1 if it is not found on the component
    """
    id = 1
    for component in component_port_mapping:
        if component_name == component:
            for port in component_port_mapping[component]:
                if port == port_name:
                    return id
                id += 1
            return -1
        else:
            id += len(component_port_mapping[component])
    return -1


def make_component_string(component_name, port_names_list):
    """
    Makes a string for graphviz to depict the given component
    """
    global cluster_ID
    cluster_ID += 1

    # 00,48, 87  <- decimal
    num_out = len(port_names_list)
    """
    can uncomment this to customize color scheme for component nodes
    green = int(max(200 - 15.2 * num_out, 48))
    blue = int(max(200 - 11.3 * num_out, 87))
    red = 0"""
    gray = 100 + min(100, 10 * num_out)
    color_string = '#{:02X}{:02X}{:02X}'.format(gray, gray, gray)

    component_string = "\t\tnode [color=\"{color_string}\" style=\"filled\"]; {component_name};\n".format(
        color_string=color_string, component_name=component_name)
    return component_string


def make_port_string(port_name):
    """
    IDK what this does
    """
    global port_ID
    print("PortName: {}".format(port_name))
    port_string = "\t\tnode [shape=circle label=\"{port_name}\"]; Port{port_id};\n".format(
        port_name=port_name, port_id=port_ID)
    port_ID += 1
    return port_string


def make_graph(source_file_name, target_file_name):
    # parse XML
    components_ports = {}  # maps components to ports that they contain
    # maps components -> connection names -> tuple<port, port>
    ports_connections_ports = {}
    tree = ET.parse(source_file_name)
    root = tree.getroot()

    # get component names
    for instance in root.findall(instance_tag):
        name = instance.attrib[name_tag]
        components_ports[name] = []
        print("Component Name: {}".format(name))

    # get port connections
    print("\nConnections: ")
    for connection in root.findall(connection_tag):
        connection_name = connection.attrib[name_tag]
        target = connection.find("./{}".format(target_tag))
        source = connection.find("./{}".format(source_tag))
        target_component = target.attrib[component_tag]
        source_component = source.attrib[component_tag]
        target_port = target.attrib[port_tag]
        source_port = source.attrib[port_tag]
        print("source: {}, target: {}, name: {}".format(
            source_component, target_component, connection_name))

        source_component_port_pair = (source_component, source_port)
        target_component_port_pair = (target_component, target_port)

        # log ports
        if source_port not in components_ports[source_component]:
            components_ports[source_component].append(source_port)
        if target_port not in components_ports[target_component]:
            components_ports[target_component].append(target_port)

        # log connection
        if source_component_port_pair not in ports_connections_ports:
            ports_connections_ports[source_component_port_pair] = {}
        ports_connections_ports[source_component_port_pair][connection_name] = target_component_port_pair

    print("\nComponents and their ports:\n")
    for component in components_ports:
        print("\n{}".format(component))
        for port in components_ports[component]:
            print("\t{}".format(port))

    num_connections = 0
    for port_info in ports_connections_ports:
        num_connections += len(ports_connections_ports[port_info])
    print("Num Connections: {}".format(num_connections))

    # turn parsed XML into graphViz text
    output_file = open(target_file_name, 'w+')
    start_index = 0
    if source_file_name.rfind("/") >= 0:
        start_index = source_file_name.rfind("/")
    elif source_file_name.rfind("\\") >= 0:
        start_index = source_file_name.rfind("\\")
    source_file_name_noending = source_file_name[start_index:source_file_name.rfind(
        ".")]

    all_ports = []
    for component in components_ports:
        all_ports.extend(components_ports[component])

    # write heading
    output_file.write("digraph G {{ label=\"{}\"\n".format(
        source_file_name_noending))

    # write subgraphs
    for component in components_ports:
        output_file.write(make_component_string(
            component, components_ports[component]))

    output_file.write("\n")
    # write connections
    for port_info in ports_connections_ports:
        for connection_name in ports_connections_ports[port_info]:
            target_port_info = ports_connections_ports[port_info][connection_name]
            source_component = port_info[0]
            source_port = port_info[1]
            target_component = target_port_info[0]
            target_port = target_port_info[1]

            # id1 = find_unique_port_ID(
            #     source_component, source_port, components_ports)
            # id2 = find_unique_port_ID(
            #     target_component, target_port, components_ports)
            output_file.write("\t{source_comp} -> {dest_comp}[label={connection_name} color=\"#646464;0.5:#C8C8C8\"];\n".format(
                source_comp=source_component, dest_comp=target_component, connection_name=connection_name))

    # write closing curly brace
    output_file.write("}\n")
    output_file.close()

    # run graphViz
    output_image_file = target_file_name[:target_file_name.rfind(".")] + ".jpg"
    subprocess.run(["dot", target_file_name, "-Tjpg", "-o", output_image_file])


if __name__ == '__main__':
    target_file_name = "graphviz.txt"

    if len(sys.argv) < 2:
        print("Please specify a source file name.")
        exit(1)

    source_file_name = sys.argv[1]
    if len(sys.argv) > 2:
        target_file_name = sys.argv[2]
        if target_file_name.rfind("."):
            print(
                "File must have a file extension. An image will be made with a .jpg extension")
            exit(1)
    make_graph(source_file_name, target_file_name)
