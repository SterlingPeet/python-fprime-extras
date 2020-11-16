from ..core.file import ExtrasFile
from lxml import etree


def normalize(filename):
    xml_file = ExtrasFile(filename)
    xml_tree = etree.parse(xml_file)
    print("Normalizing file {}".format(filename))
    xml_tree.write(xml_file, xml_declaration=True,
                   encoding='UTF-8', pretty_print=True)
