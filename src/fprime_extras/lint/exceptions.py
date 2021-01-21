

class Error(Exception):
    """Base exception for rule handling exceptions to inherit from."""

    def __init__(self, msg=None):
        if msg is None:
            msg = 'An error occured in the Linter.'
        super(Error, self).__init__(msg)


class RuleViolationError(Error):
    """Exception that is thrown when a rule violation is discovered."""

    def __init__(self, ident: str, line: int = None, msg: str = None):
        if line is None:
            line = 0
        if msg is None:
            'A rule was violated during the linting process.'
        super(RuleViolationError, self).__init__(msg)
        self.ident = ident
        self.line = line


class CompositeRuleViolationError(RuleViolationError):
    """Exception container for holding a batch of errors that could be
    generated from the same rule-checking sequence.
    """

    def __init__(self, ident: str, exceptions: list, line: int = None, msg: str = None):
        if msg is None:
            msg = 'Multiple ({}) rule violation exceptions contained in this exception'.format(
                len(exceptions))
        super(CompositeRuleViolationError, self).__init__(ident, msg)
        self.exceptions = exceptions
        self.line = line
