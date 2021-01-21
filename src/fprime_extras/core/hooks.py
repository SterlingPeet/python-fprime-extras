import logging as _logging

_log = _logging.getLogger(__name__)


class HookRegistry(object):
    __DB = {}

    @property
    def db(self):
        return type(self).__DB

    @classmethod
    def define(cls, name=None):
        """Define a hook"""
        if name is not None:
            _log.debug('Adding hook definition \'%s\' to database', name)
            cls.__DB[name] = []
            # TODO: allow multiple calls to define the same hook, but
            #       don't reset the registered callbacks

    @classmethod
    def register(cls, name=None, callback=None, weight=100):
        """register a callback to run when a hook is called"""
        if name is not None and callback is not None:
            _log.debug('Adding callback %s to hook \'%s\'', callback, name)
            cls.__DB[name].append(callback)
            # TODO: create/define hook if not in database
            # TODO: order callbacks by weight, somehow

    @classmethod
    def __call__(cls, name=None):  # -> List of Callables
        return cls.__DB[name]


if __name__ == "__main__":
    hook_db = HookRegistry()
    hook_db.define('test1')
    hook_db.define('test2')
    _log.warning(hook_db.db)

    def hook_callback():
        pass

    hook_db.register('test1', hook_callback)
    _log.warning(hook_db.db)
