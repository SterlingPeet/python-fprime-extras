from .base import AbstractRule
from .registry import RuleListFactory


@RuleListFactory.register()
class RuleXmlCheckValidRelaxNGSchemaPI(AbstractRule):
    """Check the input XML file for a PI that has a valid path to a """
    __tags = ['xml', 'fixable']

    @property
    def tags(self):
        return self.__tags

    @property
    def fixable(self):
        for tag in cls.__tags:
            if tag == 'fixable':
                return True
        return False
