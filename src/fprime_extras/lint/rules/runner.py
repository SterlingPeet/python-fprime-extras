from ...core.file import ExtrasFile
from ...core.hooks import HookRegistry
from .registry import RuleListRegistry


class RuleRunner(object):
    """Run a set of rules on a file, at progressive stages."""

    def __init__(self):
        self._hook_reg = HookRegistry()
        self.filename = None
        self.extras_file = None

    def run(self, name: str) -> None:
        for rule in self._hook_reg(name):
            rule(self.extras_file)


class RuleRunnerFactory(object):
    """Factory object to configure rules to be run agains a file."""

    def construct(self, extras_file: ExtrasFile) -> RuleRunner:
        runner = RuleRunner()
        runner.extras_file = extras_file
        for item in RuleListRegistry.db:
            runner.rule_list.append(item())
        return runner
