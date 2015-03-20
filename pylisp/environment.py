from __future__ import unicode_literals

import operator


class Environment(dict):
    def __init__(self, dikt=None, parent=None):
        super(Environment, self).__init__(dikt=None)
        dikt = dikt or {}
        self.parent = parent
        self.update(dikt)

    def lookup(self, s):
        if s in self:
            return self[s]
        if self.parent:
            return self.parent.lookup(s)
        raise ValueError(s)


def std_environment():
    env = Environment()
    env.update({
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
        '^': operator.pow,
    })
    return env

global_env = std_environment()
