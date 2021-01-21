import lxml.etree as etree
from lxml.etree import XMLSyntaxError

from ...core.hooks import HookRegistry as hooks
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry

slug = 'xml-document-not-valid'


@RuleListRegistry.register()
class RuleValidXmlDocument(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/raw_file_rules', cls())

    def __call__(self, config, extras_file):
        xml_tree = None
        try:
            xml_tree = etree.parse(extras_file)  # noqa: F841
            # TODO: this should be reset using a public interface
            extras_file._orig_contents_pos = 0
            extras_file._orig_contents_lines_pos = 0
        except XMLSyntaxError as e:
            note = Notification(filename=extras_file.full_filename,
                                rule_slug=slug,
                                description=e.msg,
                                line_number=e.position[0],
                                column=e.position[1],
                                severity=LintSeverity.CRITICAL
                                )
            return [note]
        return []

    def fix(self):
        pass

    def reset(self):
        pass
