import functools

from .base import AbstractRule


class RuleListFactory:
    """Class for building a rule list to run against a model."""

    registry = []
    """Registry of all rules available to check *some* model."""

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
            #     print('Rule is already in the registry, replacing with new implementation'.format(rule_number))
            if wrapped_class in cls.registry:
                print("This rule: {} already registered.".format(
                    wrapped_class.__name__))
            cls.registry.append(wrapped_class)
            # print("Registered {}.".format(wrapped_class.__name__))
            # print("Length of registry: {}".format(len(cls.registry)))
            # if wrapped_class in cls.registry:
            #     print("This rule successfully registered.")
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
        for rule in cls.registry:
            flag = True
            for tag in tags:
                if tag not in rule.tags:
                    flag = False
            if flag:
                rule_list.append(rule)
        return rule_list
