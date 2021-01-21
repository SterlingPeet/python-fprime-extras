import functools
import importlib
import logging as _logging
import pkgutil
from types import ModuleType as Module
from typing import Iterable

from . import _current_module as base_module
from .base import AbstractRule

try:  # Python 3.6 moved ModuleInfo from inspect to pkgutil
    from pkgutil import ModuleInfo
except ImportError:
    from inspect import ModuleInfo

_log = _logging.getLogger(__name__)


def _iter_namespace(ns_pkg: Module) -> Iterable[ModuleInfo]:
    """Internal helper function for loading namespace packages."""
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


class MetaRuleListRegistry(type):
    """This meta class sets up the mechanisms needed for registry
    database access using the python property syntax.  The strategy is
    borrowed from
    https://stackoverflow.com/questions/5189699/how-to-make-a-class-property
    """

    @property
    def db(cls):
        if cls._discovered_rule_modules is None:
            cls._discovered_rule_modules = {
                name: importlib.import_module(name)
                for finder, name, ispkg
                in _iter_namespace(base_module)
                # need to split on '.' and check that last field
                if name.split('.')[-1].startswith('rule_')
            }
        return cls._db


class RuleListRegistry(object, metaclass=MetaRuleListRegistry):
    """This registery is the oracle of all linter rules to run on a file
    or model.

    The registery uses lazy instatiation to populate the database of
    rules.  This strategy, while more complicated, defers the loading
    process until the first time a rule is needed.  This means that the
    core program and other sub-commands do not need to wait for this
    database to be populate, especially useful if the executable is
    being invoked for e.g.: tab completion purposes.



    TODO: Explain the interface of a rule?  Maybe point to the rule ABC...
    TODO: Explain how internal rules are loaded
    TODO: Explain how to augment the linter with custom rules.
    """

    # This dictionary contains an entry for every rule, which are discovered
    # by looking for every submodule in the current namespace, and keeping
    # only the modules pre-fixed by 'rule_'.  This dynamically loads the
    # packed rule set, and each rule registers with the
    # ``registry.RuleListRegistry`` as it is loaded.
    _discovered_rule_modules = None
    _db = []
    """Registry of all rules available to check *some* model."""

    @property
    def db(self):
        return type(self).db

    @classmethod
    def register(cls) -> AbstractRule:
        """ Class method to register linter rule class to the internal registry.

        Returns:
            The Rule class itself.
        """
        @functools.wraps(cls)
        def inner_wrapper(wrapped_class: AbstractRule) -> AbstractRule:
            # if rule_number in cls.registry:
            #     # logger.warning('Executor %s already exists. Will replace it', name)
            #     _log.warning('Rule is already in the registry, replacing with new implementation'.format(rule_number))
            if wrapped_class in cls.db:
                _log.warning("This rule: {} already registered.".format(
                    wrapped_class.__name__))
            cls.db.append(wrapped_class)
            _log.info("Registered {}.".format(wrapped_class.__name__))
            # _log.debug("Length of registry: {}".format(len(cls.registry)))
            # if wrapped_class in cls.registry:
            #     _log.debug("This rule successfully registered.")
            return wrapped_class

        return inner_wrapper

    @classmethod
    def rules(cls, tags: list = []) -> list:
        """ Factory command to create a list of rules.
        This method filters the registry of rules for rules with tagas
        matching the list provided.  An empty list will yield the entire
        registry of rules.
        Args:
            tags (list): A list of tags that all rules should contain
        Returns:
            A list containing all the rules with matching tags
        """
        rule_list = []
        for rule in cls.db:
            flag = True
            for tag in tags:
                if tag not in rule.tags:
                    flag = False
            if flag:
                rule_list.append(rule)
        return rule_list
