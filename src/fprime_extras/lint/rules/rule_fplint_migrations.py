import logging
from pathlib import Path

import fprime_extras.lint.migrations.checks  # noqa: F401

from ...core.hooks import HookRegistry as hooks
from ..migrations.check import CheckBase
from ..migrations.check import CheckResult
from ..migrations.config import ConfigurationException
from ..migrations.config import load_configuration
from ..migrations.model.patcher import InconsistencyException
from ..migrations.model.patcher import load_patched_topology
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry

log = logging.getLogger(__name__)


@RuleListRegistry.register()
class FPlintMigrations(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def config_args(cls):
        return CheckBase.get_all_extra_args().items()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/config_args', cls.config_args)
        hooks.register('fprime_extras/lint/fprime_model_rules', cls())

    def __call__(self, config, extras_file, doc_model, fprime_model):
        # Try to validate against RNG schema
        # Apparently we need to import at least one check, else none
        # are found...
        from ..migrations.checks.connected import PortConnections  # noqa: F401

        notifications = []
        topology_model = None

        # Loads configuration and check that configuration matches available code
        try:
            # Note: load config after all imports have been done
            conf = load_configuration(config.config, list(
                CheckBase.get_all_identifiers([])))
        except ConfigurationException as exc:
            log.error("[ERROR] {}".format(exc))
            return []  # let other rules run

        # Try to load the model and  report errors if it fails to load a consistent model
        try:
            topology_model = load_patched_topology(
                Path(extras_file.full_filename))
        except InconsistencyException as inc:
            log.info("Expected Topology: Loading model detected specification error {}".format(
                inc))
            return notifications

        # Borrowed from CheckBase.run_all
        excluded = conf.get("exclusions", [])
        log.debug('excluded:: {}'.format(excluded))
        filters = conf.get("filters", [])
        log.debug('filters:: {}'.format(filters))
        arguments = config
        checkers = CheckBase.get_checkers(excluded)
        log.info("[FP-LINT] Found {} checks".format(len(checkers)))
        all_clear = True
        for checker in checkers:
            try:
                needed_args = [arg.replace(
                    "-", "_") for arg in checker.get_extra_arguments().keys()]
                filled_args = [getattr(arguments, needed, None) for needed in needed_args if getattr(
                    arguments, needed, None) is not None]
                if needed_args and arguments is None or len(needed_args) != len(filled_args):
                    log.warning(
                        "[FP-LINT] '{}' missing needed args. Skipping".format(checker.__name__))
                    continue
                log.info(
                    "[FP-LINT] Running check '{}'".format(checker.__name__))
                result = CheckResult(checker.get_identifiers())
                result = checker().run(result, topology_model, filled_args)
                problems = result.get_filtered_problems(filters)
                for problem in problems:
                    description = '{} {}'.format(
                        problem['module'], problem['message'])
                    line = self._synthesize_line_info(
                        extras_file, doc_model, problem['module'])
                    note = Notification(filename=extras_file.full_filename,
                                        rule_slug=problem['identifier'],
                                        description=description,
                                        line_number=line[0],
                                        column=line[1],
                                        severity=LintSeverity.ERROR  # TODO: fix
                                        )
                    notifications.append(note)
                all_clear = all_clear and not problems
            except Exception as exc:
                log.error("[ERROR] {} failed: {}".format(
                    checker.__name__, exc))
                all_clear = False
        return notifications

    def _synthesize_line_info(self, extras_file, doc_model, identifier):
        ret = (len(extras_file._orig_contents_lines), 0)
        doc_root = doc_model.getroot()
        if hasattr(self, '_component_list') is False:
            self._component_list = [c for c in doc_root if c.tag == 'instance']
        if hasattr(self, '_connection_list') is False:
            self._connection_list = [
                c for c in doc_root if c.tag == 'connection']
        line_mod = identifier.split('.')
        line_port = line_mod[2].split(':')
        top_name = line_mod[0]
        comp_name = line_mod[1]
        port_name = line_port[0]
        port_num = line_port[1]
        if doc_root.get('name') == top_name:
            # First try, get component instance line
            for comp in self._component_list:
                if comp.get('name') == comp_name:
                    ret = (comp.sourceline, 0)
            # Next Look for any connections with this component
            port_list = []
            for conn in self._connection_list:
                for comp in conn:
                    if comp.get('component') == comp_name:
                        port_list.append(comp)
            # Find if there is a port with the correct name and number
            for port in port_list:
                if port.get('port') == port_name:
                    if port.get('num') == port_num:
                        ret = (port.sourceline, 0)
        return ret

    def fix(self):
        pass

    def reset(self):
        pass
