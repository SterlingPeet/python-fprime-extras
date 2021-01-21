import logging
import os

import lxml.etree as etree
from lxml.etree import DocumentInvalid

from ...core.hooks import HookRegistry as hooks
from .base import AbstractRule
from .base import LintSeverity
from .base import Notification
from .registry import RuleListRegistry

log = logging.getLogger(__name__)
slug = 'check-rng-schema'


@RuleListRegistry.register()
class RuleXmlCheckValidRelaxNGSchemaPI(AbstractRule):
    """Check if input XML file can be parsed."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register_hook_callbacks(cls):
        hooks.register('fprime_extras/lint/document_model_rules', cls())

    def __call__(self, config, extras_file, doc_model):
        # Try to validate against RNG schema
        notifications = []
        pi_list = doc_model.xpath('//processing-instruction()')
        schema_pi = None
        for pi in pi_list:
            # TODO: pi.sourceline is the line number of the pi
            if pi.target == 'xml-model':
                schema_pi = pi
            if pi.target == 'oxygen':
                try:
                    # if the PI name is "oxygen" and it has a field called
                    # "RNGSchema", then we know it was a previous and outdated
                    # form of the schema definition
                    # TODO: emit a notification for this scenario
                    if pi.get('RNGSchema'):
                        log.warning(
                            '** WARNING: Outdated Schema definition style!')
                        schema_pi = pi
                except Exception:
                    pass

        rng_filename = None
        rng_exists = False
        if schema_pi is None:
            log.warning('** WARNING: No Schema PI detected!')
        elif schema_pi.target == 'xml-model':
            log.info('RNG Schema type: {}'.format(schema_pi.get('type')))
            log.info('RNG Namespace: {}'.format(
                schema_pi.get('schematypens')))
            log.info('RNG Validation File: {}'.format(schema_pi.get('href')))
            rng_filename = extras_file.resolve_relative_path(
                schema_pi.get('href'))
            log.info('RNG File Resolved: {}'.format(rng_filename))
            if os.path.exists(rng_filename):
                log.info('File Exists!')
                rng_exists = True
            else:
                log.info('RNG Path is invalid...')
                # TODO: this is its own notification
        elif schema_pi.target == 'oxygen':
            log.info('RNG Schema type: {}'.format(schema_pi.get('type')))
            log.info('RNG Validation File: {}'.format(
                schema_pi.get('RNGSchema')))
            rng_filename = extras_file.resolve_relative_path(
                schema_pi.get('RNGSchema')[5:])
            log.info('RNG File Resolved: {}'.format(rng_filename))
            if os.path.exists(rng_filename):
                log.debug('File Exists!')
                rng_exists = True
            else:
                log.info('RNG Path is invalid...')
                # TODO: this is its own notification

        if rng_exists:
            log.info('Validating file against provided schema.')
            relaxng = etree.RelaxNG(file=rng_filename)
            try:
                relaxng.assertValid(doc_model)
            except DocumentInvalid:
                this_line = None
                for elog in relaxng.error_log:
                    log.debug(elog)
                    if this_line is None:
                        this_line = elog.line
                    note = Notification(filename=extras_file.full_filename,
                                        rule_slug=slug,
                                        description=elog.message,
                                        line_number=elog.line,
                                        column=elog.column,
                                        severity=LintSeverity.CRITICAL
                                        )
                    if note.line_number == this_line:
                        notifications.append(note)
        else:
            log.info('No RNG file found.')
            note = Notification(filename=extras_file.full_filename,
                                rule_slug=slug,
                                description='No RNG Schema found in Processing Instructions.',
                                line_number=2,
                                column=0,
                                severity=LintSeverity.ERROR
                                )
            notifications.append(note)
        return notifications

        # try:
        #     # schematron_file = base_file.resolve_relative_path('../../../../Autocoders/Python/schema/default/channel_id_schematron.rng')
        #     schematron_file = base_file.resolve_relative_path('../../../../Autocoders/Python/schema/default/comp_uniqueness_schematron.rng')  # noqa: E501
        #     # schematron_file = base_file.resolve_relative_path('../../../../Autocoders/Python/schema/default/channel_id_schematron.rng')
        #     cli_log.info('Loading Schematron file: {}'.format(schematron_file))
        #     schematron = etree.Schematron(file=schematron_file)
        #     schematron.assertValid(xml_tree)
        #     cli_log.info('Validation complete.')
        # except DocumentInvalid as e:
        #     # cli_log.error(e)
        #     cli_log.error('\r\n*** A Schematron validation error has occured: \r\n')
        #     elog = schematron.error_log
        #     cli_log.error(elog)

    def fix(self):
        pass

    def reset(self):
        pass
