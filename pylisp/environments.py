from __future__ import unicode_literals

import math
import operator as op
from pylisp import Procedure
from read import parse
from utils import Colors

global_env = None

std_procedures = {
    'fact': '''(lambda (x)
                 (if (< x 2) x
                   (* x (fact (- x 1)))))''',
    'fib': '''(lambda (x)
                (if (< x 2) x
                  (+ (fib (- x 1)) (fib (- x 2)))))''',
}


class Symbol(object):
    def __init__(self, v):
        self.value = v

    def __repr__(self):
        return Colors.blue(self.value)

    def __eq__(self, v):
        return self.value == v


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

    def eval(self, expr):
        if isinstance(expr, Symbol):
            _, val = self.lookup(expr.value)
            return val
        elif not isinstance(expr, list):
            return expr
        elif expr[0] == 'gethash':
            key, table = expr[1], self.eval(expr[2])
            if isinstance(key, Symbol):
                # HACK: until we have strings, fake it here
                if (key.value[0], key.value[-1]) == ('"', '"'):
                    key = key.value
                else:
                    key = self.eval(key)
            else:
                key = self.eval(key)
            return table.get(key)
        elif expr[0] == 'lambda':
            arglist = expr[1]
            body = expr[2]
            return Procedure(arglist, body, self)
        elif expr[0] == 'define':
            sym = expr[1]
            if sym.value in self:
                raise ValueError('{} already defined in environment'.format(sym))
            val = self.eval(expr[2])
            self[sym.value] = val
            return val
        elif expr[0] == 'set':
            # Apparently the Lisp way is to hack a bunch of special cases in here
            place = expr[1]
            val = self.eval(expr[2])
            if isinstance(place, list) and place[0] in ['gethash']:
                if place[0] == 'gethash':
                    key, table = place[1], self.eval(place[2])
                    if isinstance(key, Symbol):
                        # HACK: until we have strings, fake it here
                        if (key.value[0], key.value[-1]) == ('"', '"'):
                            key = key.value
                        else:
                            key = self.eval(key)
                    else:
                        key = self.eval(key)
                    table[key] = val
            else:
                # Must be a Symbol
                sym = self.eval(expr[1])
                if not isinstance(sym, Symbol):
                    raise TypeError('{} is not a Symbol'.format(sym))
                if sym.value not in self:
                    raise ValueError('{} not found in environment'.format(sym))
                self[sym.value] = val
            return val
        elif expr[0] == 'if':
            try:
                _, cond, true_expr, false_expr = expr
            except ValueError:
                _, cond, true_expr = expr
                false_expr = 'None'
            return (self.eval(true_expr) if self.eval(cond)
                    else self.eval(false_expr))
        elif expr[0] == 'cond':
            # TOOD: probably not compliant
            i = 1
            while i < len(expr):
                cond, result = expr[i]
                if self.eval(cond):
                    return self.eval(result)
                i += 1
            # No conditions matched
            return None
        elif expr[0] == 'and':
            result = True
            for exp in expr[1:]:
                result = self.eval(exp)
                if result in [None, False]:
                    return None
            return result
        elif expr[0] == 'or':
            result = None
            for exp in expr[1:]:
                result = self.eval(exp)
                if result not in [None, False]:
                    return result
            return result
        elif expr[0] == 'let':
            let_forms = expr[1]
            # TODO: let is an implicit progn, there can be multiple body forms, not
            # just one
            body = expr[2] if len(expr) > 2 else None
            new_env = Environment(parent=self)
            for form in let_forms:
                new_env[form[0].value] = self.eval(form[1])
            ret = new_env.eval(body)
            if isinstance(ret, Procedure):
                # Pull the procedure out of the env belonging to `let` and place it
                # in this one, so we can still access it once the let form is
                # exited.
                # TODO: this seems really dirty -- would love to know the right way
                # to do it.
                procedure_to_name = {v: k for k, v in ret.parent_env.iteritems()
                                     if isinstance(v, Procedure)}
                if ret in procedure_to_name:
                    name = procedure_to_name[ret]
                    ret.parent_env.pop(name)
                    self[name] = ret
            return ret
        elif expr[0] == 'map':
            # TODO: probably non-conforming, can we implement this in lisp?
            proc = self.eval(expr[1])
            args_list = [self.eval(arg) for arg in expr[2:]]
            ret = [proc(*args) for args in zip(*args_list)]
            return ret
        elif expr[0] == 'seq':
            args = [self.eval(arg) for arg in expr[1:]]
            ret = range(*args)
            return ret
        elif expr[0] == 'quote':
            return expr[1]
        else:
            proc = self.eval(expr[0])
            args = [self.eval(arg) for arg in expr[1:]]
            ret = proc(*args)
            if ret is False:
                # Lisp!
                ret = None
            return ret


def std_environment():
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
        'make-hash-table': lambda: dict(),              # pylint: disable=W0108
        'True': True,
        'None': None,
        'type': type,
    })
    # env.update(vars(math))

    for proc_name, proc_code in std_procedures.iteritems():
        env[proc_name] = env.eval(parse(proc_code))
    return env


def reset_global_env():
    global global_env                         # pylint: disable=W0603
    global_env = std_environment()


reset_global_env()
