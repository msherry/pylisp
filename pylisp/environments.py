from __future__ import unicode_literals

import math
import operator as op


std_procedures = {
    'fact': '''(lambda (x)
                 (if (< x 2) x
                   (* x (fact (- x 1)))))''',
    'fib': '''(lambda (x)
                (if (< x 2) x
                  (+ (fib (- x 1)) (fib (- x 2)))))''',
}


class Environment(dict):
    def __init__(self, dikt=None, parent=None):
        super(Environment, self).__init__(dikt=None)
        dikt = dikt or {}
        self.parent = parent
        self.update(dikt)

    def lookup(self, s):
        if s in self:
            return self, self[s]
        if self.parent:
            return self.parent.lookup(s)
        raise ValueError('Symbol "{}" not found'.format(s))


def std_environment():
    from pylisp import l_eval, parse

    env = Environment()
    env.update({
        '+': lambda *x: sum(x),
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
        'list': lambda *args: list(args),
        'True': True,
        'None': None,
    })
    # env.update(vars(math))

    for proc_name, proc_code in std_procedures.iteritems():
        env[proc_name] = l_eval(parse(proc_code), env)
    return env

global_env = std_environment()
