import importlib
import pkgutil

import sys

from .registry import RuleListFactory  # noqa: F401

_current_module = sys.modules[__name__]


def _iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


discovered_rule_modules = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in _iter_namespace(_current_module)
}
