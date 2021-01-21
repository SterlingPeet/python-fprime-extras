import logging

from ...core.hooks import HookRegistry as hooks
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry

log = logging.getLogger(__name__)
slug = 'dangling-port-connections'


@RuleListRegistry.register()
class RuleDanglingPortConnections(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/document_model_rules', cls())

    def __call__(self, config, extras_file, doc_model):
        notifications = []
        if doc_model.getroot().tag == 'assembly':
            log.debug('This is a topology file.')

            top_tree = doc_model
            top_root = top_tree.getroot()

            # Make lists of tags
            tag_lists_dict = {}
            for child in top_root:
                if child.tag not in tag_lists_dict:
                    tag_lists_dict[child.tag] = []
                tag_lists_dict[child.tag].append(child)

            for key in tag_lists_dict:
                log.debug('Found {} {} elements.'.format(
                    len(tag_lists_dict[key]), key))

            # Pre-compute list of instance names for checking against
            instance_names = [i.get('name')
                              for i in tag_lists_dict['instance']]
            log.debug('\nFinding connections.')
            for conn in tag_lists_dict['connection']:
                conn_name = conn.get('name')
                source = ''
                target = ''
                flag = False
                msg = None
                for comp in conn:
                    if comp.tag == 'source':
                        source = comp.get('component')
                    if comp.tag == 'target':
                        target = comp.get('component')
                if source not in instance_names:
                    msg = 'Connection "{}" contains non-existent, dangling source "{}"'.format(
                        conn_name, source)
                    log.debug(msg)
                    flag = True
                if target not in instance_names:
                    msg = 'Connection "{}" contains non-existent, dangling target "{}"'.format(
                        conn_name, target)
                    log.debug(msg)
                    flag = True
                if flag:
                    note = Notification(filename=extras_file.full_filename,
                                        rule_slug=slug,
                                        description=msg,
                                        line_number=conn.sourceline,
                                        column=0,
                                        severity=LintSeverity.ERROR
                                        )
                    notifications.append(note)
        return notifications

    def fix(self):
        # if args.fix and flag:
        #     conn.getparent().remove(conn)
        pass

    def reset(self):
        pass
