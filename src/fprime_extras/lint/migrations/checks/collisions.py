""" Checks for port collisions

Port collisions occur on ports that are "arrays" when two inputs hooks to the same numbered port. That is:

comp1 -> comp.port[1]
comp2 -> comp.port[2]
comp3 -> comp.port[2] # Likely an error

Notes:
 - Multiple connections to port 0 of non-array ports are ignored
 - Unconnected ports are ignored
"""

import logging
from typing import Dict

from fprime_extras.lint.migrations.check import CheckBase
from fprime_extras.lint.migrations.check import CheckResult
from fprime_extras.lint.migrations.check import CheckSeverity
from fprime_extras.lint.migrations.model.patcher import Topology
from fprime_extras.lint.migrations.model.patcher import get_comp_by_name
from fprime_extras.lint.migrations.model.patcher import get_port_by_name

log = logging.getLogger(__name__)


class PortCollision(CheckBase):

    @classmethod
    def get_identifiers(self) -> Dict[str, CheckSeverity]:
        """ Returns identifiers produced here."""
        return {
            "array-port-collision": CheckSeverity.ERROR
        }

    def run(self, result: CheckResult, model: Topology, _) -> CheckResult:
        """ Runs this check """
        port_mappings = {}
        for component in model.get_comp_list():
            for port in component.get_ports():
                target_port = port.get_target_port()
                target_component = port.get_target_comp()

                # Only a check for connected ouput ports
                if port.get_direction().lower() == "input" or target_port is None or target_component is None:
                    continue
                # Get object (not name) representations
                target_comp_obj = get_comp_by_name(model, target_component)
                if target_comp_obj is not None:
                    target_port_obj = get_port_by_name(
                        target_comp_obj, target_port, port.get_target_num())
                    target_max_num = target_port_obj.get_max_number()
                    # Also ignore max numbers of 1, as they aren't arrays
                    if target_max_num is None or int(target_max_num) <= 1:
                        continue
                    standard_id = CheckBase.get_standard_identifier(
                        model, target_comp_obj, target_port_obj)
                    if standard_id in port_mappings:
                        result.add_problem("array-port-collision", "has colliding inputs",
                                           model, target_comp_obj, target_port_obj)
                    port_mappings[standard_id] = target_comp_obj
                else:
                    log.info('target component {} generated no matching object'.format(
                        target_component))
        return result
