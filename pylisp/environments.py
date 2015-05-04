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

    def eval_symbol(self, expr):
        _, val = self.lookup(expr.value)
        return val

    def eval_quote(self, expr):
        return expr[1]

    def eval_gethash(self, expr):
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

    def eval_lambda(self, expr):
        arglist = expr[1]
        body = expr[2]
        return Procedure(arglist, body, self)

    def eval_define(self, expr):
        sym = expr[1]
        if sym.value in self:
            raise ValueError('{} already defined in environment'.format(sym))
        val = self.eval(expr[2])
        self[sym.value] = val
        return val

    def eval_set(self, expr):
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

    def eval_if(self, expr):
        try:
            _, cond, true_expr, false_expr = expr
        except ValueError:
            _, cond, true_expr = expr
            false_expr = 'None'
        return (self.eval(true_expr) if self.eval(cond)
                else self.eval(false_expr))

    def eval_cond(self, expr):
        # TOOD: probably not compliant
        i = 1
        while i < len(expr):
            cond, result = expr[i]
            if self.eval(cond):
                return self.eval(result)
            i += 1
        # No conditions matched
        return None

    def eval_and(self, expr):
        result = True
        for exp in expr[1:]:
            result = self.eval(exp)
            if result in [None, False]:
                return None
        return result

    def eval_or(self, expr):
        result = None
        for exp in expr[1:]:
            result = self.eval(exp)
            if result not in [None, False]:
                return result
        return result

    def eval_let(self, expr):
        let_forms = expr[1]
        body_forms = expr[2:] if len(expr) > 2 else []
        new_env = Environment(parent=self)
        for form in let_forms:
            new_env[form[0].value] = self.eval(form[1])

        ret = None
        for body in body_forms:
            # TODO: reuse this for progn?
            ret = new_env.eval(body)
            if isinstance(ret, Procedure):
                # Pull the procedure out of the env belonging to `let` and
                # place it in this one, so we can still access it once the let
                # form is exited.
                # TODO: this seems really dirty -- would love to know the right
                # way to do it.
                # TODO: SICP 5.2.5 has the right way to do this -- use that.
                procedure_to_name = {v: k for k, v in ret.parent_env.iteritems()
                                     if isinstance(v, Procedure)}
                if ret in procedure_to_name:
                    name = procedure_to_name[ret]
                    ret.parent_env.pop(name)
                    self[name] = ret
        return ret

    def eval_map(self, expr):
        # TODO: probably non-conforming, can we implement this in lisp?
        proc = self.eval(expr[1])
        args_list = [self.eval(arg) for arg in expr[2:]]
        ret = [proc(*args) for args in zip(*args_list)]
        return ret

    def eval_seq(self, expr):
        args = [self.eval(arg) for arg in expr[1:]]
        ret = range(*args)
        return ret

    def eval_proc(self, expr):
        proc = self.eval(expr[0])
        args = [self.eval(arg) for arg in expr[1:]]
        ret = proc(*args)
        if ret is False:
            # Lisp!
            ret = None
        return ret

    def eval(self, expr):
        if isinstance(expr, Symbol):
            return self.eval_symbol(expr)
        elif not isinstance(expr, list):
            return expr
        elif expr[0] == 'quote':
            return self.eval_quote(expr)
        elif expr[0] == 'gethash':
            return self.eval_gethash(expr)
        elif expr[0] == 'lambda':
            return self.eval_lambda(expr)
        elif expr[0] == 'define':
            return self.eval_define(expr)
        elif expr[0] == 'set':
            return self.eval_set(expr)
        elif expr[0] == 'if':
            return self.eval_if(expr)
        elif expr[0] == 'cond':
            return self.eval_cond(expr)
        elif expr[0] == 'and':
            return self.eval_and(expr)
        elif expr[0] == 'or':
            return self.eval_or(expr)
        elif expr[0] == 'let':
            return self.eval_let(expr)
        elif expr[0] == 'map':
            return self.eval_map(expr)
        elif expr[0] == 'seq':
            return self.eval_seq(expr)
        else:
            return self.eval_proc(expr)


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
