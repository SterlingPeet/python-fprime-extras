import logging

from ...core.hooks import HookRegistry as hooks
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry
from ...core.util import find_fprime

from pathlib import Path
import os, sys
import lxml.etree as etree
from lxml.etree import XMLSyntaxError

log = logging.getLogger(__name__)
port_slug = 'invalid-port-type'
root_slug = 'invalid-fprime-structure'
import_types_slug = 'invalid-port-type-import'


@RuleListRegistry.register()
class RuleValidPortType(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/document_model_rules', cls())

    def __call__(self, config, extras_file, doc_model):
        notifications = []
        fprime_path = config.fprime_root
        if fprime_path is None or not os.path.exists(fprime_path):
            log.info("Received input root of {} which is invalid. Searching for Fprime root instead".format(fprime_path))
            if fprime_path is not None:
                msg = "{} does not exist. Searching for Fprime root as parent of component.".format(fprime_path)
            fprime_path = find_fprime(Path(extras_file.full_filename))
        if fprime_path is None:
            descr = "Cannot check port types. Missing valid Fprime path."
            descr += " Please execute command from Fprime subdirectory or pass Fprime path as arg."
            note = Notification(filename=extras_file.full_filename,
                                rule_slug=root_slug,
                                description=descr,
                                line_number=0,
                                column=0,
                                severity=LintSeverity.WARNING
                                )
            notifications.append(note)
        if doc_model.getroot().tag == 'component' and fprime_path is not None:
            log.debug('This is a component file.')

            top_tree = doc_model
            top_root = top_tree.getroot()

            component_namespace = top_root.get("namespace")

            has_ports = False
            # Make lists of tags
            tag_lists_dict = {}
            for child in top_root:
                if child.tag not in tag_lists_dict:
                    tag_lists_dict[child.tag] = []
                    if child.tag == 'ports':
                        has_ports = True
                tag_lists_dict[child.tag].append(child)

            if has_ports:
                port_list = [p for p in tag_lists_dict['ports'][0] if p.tag == 'port']
                import_list = tag_lists_dict['import_port_type']
                imported_types, notes = self.get_imported_types(import_list, fprime_path, extras_file)
                if len(notes) > 0:
                    notifications.extend(notes)
                    return notifications

                for port in port_list:
                    port_type = port.get('data_type')
                    full_port_type = component_namespace + "::" + port_type
                    # check if referenced type was imported. Check for local and global namespace
                    valid = port_type in imported_types or full_port_type in imported_types
                    if not valid:
                        name = port.get('name')
                        msg = 'Port "{}" specifies invalid type "{}". Imported types are {}.'
                        msg = msg.format(name, port_type, imported_types)
                        note = Notification(filename=extras_file.full_filename,
                                            rule_slug=port_slug,
                                            description=msg,
                                            line_number=port.sourceline,
                                            column=0,
                                            severity=LintSeverity.CRITICAL
                                            )
                        notifications.append(note)
        return notifications

    def fix(self):
        # if args.fix and flag:
        #     conn.getparent().remove(conn)
        pass

    def reset(self):
        pass

    def get_imported_types(self, import_list, fprime_path, extras_file):
        """
        import_list: list of import_port_type etree elements
        fprime_path: path to the fprime root
        extras_file: file that imports the given files

        parses the imported files and returns a hash set of their full type names as strings.
        Will also return any critical notifications associated with parsing the imported types
        """
        imported_types = set()
        notifications = []
        for imp in import_list:
            import_path = os.path.join(fprime_path, imp.text)
            if os.path.exists(import_path):
                try:
                    xml_tree = etree.parse(import_path)
                    root = xml_tree.getroot()
                    if root.tag == "interface":
                        name = root.get("name")
                        namespace = root.get("namespace")
                        full_name = namespace + "::" + name
                        imported_types.add(full_name)
                        log.info("Found port type: {}".format(full_name))
                    else:
                        note = Notification(filename=extras_file.full_filename,
                                            rule_slug=import_types_slug,
                                            description="Component imported invalid port type: {}".format(imp.text),
                                            line_number=imp.sourceline,
                                            column=0,
                                            severity=LintSeverity.CRITICAL
                                            )
                        notifications.append(note)
                except XMLSyntaxError as e:
                    note = Notification(filename=extras_file.full_filename,
                                        rule_slug=import_types_slug,
                                        description=e.msg,
                                        line_number=imp.sourceline,
                                        column=e.position[1],
                                        severity=LintSeverity.CRITICAL
                                        )
                    notifications.append(note)
            else:
                note = Notification(filename=extras_file.full_filename,
                                    rule_slug=import_types_slug,
                                    description="Component imported file ({}) which does not exist.".format(import_path),
                                    line_number=imp.sourceline,
                                    column=0,
                                    severity=LintSeverity.CRITICAL
                                    )
                notifications.append(note)

        return imported_types, notifications
