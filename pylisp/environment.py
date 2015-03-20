from __future__ import unicode_literals

import math
import operator as op


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
        raise ValueError('{} not found'.format(s))


def std_environment():
    env = Environment()
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.div,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        '^': op.pow,
        '%': op.mod,
    })
    env.update(vars(math))
    return env

global_env = std_environment()
