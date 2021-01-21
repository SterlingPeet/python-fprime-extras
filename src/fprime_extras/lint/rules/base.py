from abc import ABCMeta
from abc import abstractmethod
from enum import Enum

# class HookCallbackDict(TypedDict):
#     pre_load: Callable[[str], None]
#     raw_file: Callable[[ExtrasFile], None]
#     xml_tree: Callable[[type(etree)], None]
#     local_model: Callable[[ExtrasFile], None]  # TODO: should take in a model
#     global_model: Callable[[ExtrasFile], None]  # TODO: should take in a model


class LintSeverity(Enum):
    """Indicator of lint severity."""
    WARNING = 0
    ERROR = 1
    CRITICAL = 2


class AbstractRule(metaclass=ABCMeta):
    """Base class for defining linter rules."""

    # def __init__(self):
    #     self._hooks = HookCallbackDict()
    #     _log.debug('test2')

    @classmethod
    def register_hook_callbacks(cls):
        raise NotImplementedError()

    @abstractmethod
    def fix(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class Notification(object):
    """Object to hold lint notification data."""
    filename = None
    rule_slug = None
    line_number = None
    column = None
    description = None
    severity = None
    to_str = '{filename} (L{line_number},C{column}): {rule_slug} -> {description} [{severity}]'

    def __init__(self, filename, rule_slug, line_number=None, column=None, description=None, severity=None):
        self.filename = filename
        self.rule_slug = rule_slug
        self.description = description
        self.severity = severity
        self.line_number = line_number
        if line_number is None:
            self.line_number = 0
        self.column = column
        if column is None:
            self.column = 0

    def __str__(self):
        return self.to_str.format(filename=self.filename,
                                  rule_slug=self.rule_slug,
                                  line_number=self.line_number,
                                  column=self.column,
                                  description=self.description,
                                  severity=self.severity)

    def __repr__(self):
        rep = []
        rep.append('{}.Notification('.format(__name__))
        rep.append('filename={}, '.format(self.filename))
        rep.append('rule_slug={}, '.format(self.rule_slug))
        rep.append('line_number={}, '.format(self.line_number))
        rep.append('column={}, '.format(self.column))
        rep.append('description=\'{}\', '.format(self.description))
        rep.append('severity={}'.format(self.severity))
        rep.append(')')
        return ''.join(rep)
