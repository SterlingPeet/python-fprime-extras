import logging as _logging

from lxml import etree

from ..core.file import ExtrasFile

_log = _logging.getLogger(__name__)


def normalize(filename):
    xml_file = ExtrasFile(filename)
    xml_tree = etree.parse(xml_file)
    _log.info("Normalizing file {}".format(filename))
    xml_tree.write(xml_file, xml_declaration=True,
                   encoding='UTF-8', pretty_print=True)
