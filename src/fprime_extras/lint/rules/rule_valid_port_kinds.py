import logging

from ...core.hooks import HookRegistry as hooks
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry

log = logging.getLogger(__name__)
slug = 'invalid-port-kind'
# TODO: import following list from model instead of defining it here.
port_kinds = ['output', 'sync_input', 'async_input', 'guarded_input']


@RuleListRegistry.register()
class RuleValidPortKinds(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/document_model_rules', cls())

    def __call__(self, config, extras_file, doc_model):
        notifications = []
        if doc_model.getroot().tag == 'component':
            log.debug('This is a component file.')

            top_tree = doc_model
            top_root = top_tree.getroot()

            has_ports = False
            # Make lists of tags
            tag_lists_dict = {}
            for child in top_root:
                if child.tag not in tag_lists_dict:
                    tag_lists_dict[child.tag] = []
                    if child.tag == 'ports':
                        has_ports = True
                tag_lists_dict[child.tag].append(child)

            # for key in tag_lists_dict:
            #     log.debug('Found {} {} elements.'.format(
            #         len(tag_lists_dict[key]), key))

            if has_ports:
                port_list = [p for p in tag_lists_dict['ports'][0] if p.tag == 'port']
                for port in port_list:
                    port_kind = port.get('kind')
                    valid = False
                    for kind in port_kinds:
                        if kind == port_kind:
                            valid = True
                    if not valid:
                        name = port.get('name')
                        msg = 'Port "{}" specifies invalid kind "{}", must be one of {}'
                        msg = msg.format(name, port_kind, port_kinds)
                        note = Notification(filename=extras_file.full_filename,
                                            rule_slug=slug,
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
