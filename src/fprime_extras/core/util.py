import logging
from pathlib import Path


class ConsoleLoggingContext:
    """This logging context class is used to temporarily change the
    the log configuration and handler for a limited time [or context].

    Default to INFO level.
    """

    def __init__(self, logger, level=None, handler=None, close=True):
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close

    def __enter__(self):
        if self.level is None:
            self.level = logging.INFO
        self.old_level = self.logger.level
        self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()


def find_fprime(cwd: Path) -> Path:
    """
    Finds F prime by recursing parent to parent until a matching directory is found.
    Returns None if no fprime root is found
    """
    needle = Path("cmake/FPrime.cmake")
    path = cwd.resolve()
    while path != path.parent:
        if Path(path, needle).is_file():
            return path
        path = path.parent
