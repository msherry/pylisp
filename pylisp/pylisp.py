#!/usr/bin/env python

from __future__ import unicode_literals

from utils import Colors
from repl import read_loop


class Procedure(object):

    # TODO: can't move this into its own file where it has to import pylisp, or
    # the `isinstance(expr, Symbol)` test fails -- __main__.Symbol !=
    # pylisp.Symbol

    def __init__(self, arglist, body, parent_env):
        self.arglist = arglist
        self.body = body
        self.parent_env = parent_env

    def __call__(self, *args):
        env = Environment(parent=self.parent_env)
        for arg, val in zip(self.arglist, args):
            assert isinstance(arg.value, basestring)
            env[arg.value] = val
        return l_eval(self.body, env=env)


class Symbol(object):
    def __init__(self, v):
        self.value = v

    def __repr__(self):
        return Colors.blue(self.value)

    def __eq__(self, v):
        return self.value == v


def atom(x):
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return Symbol(x)


def tokenize(chars):
    special = "()'"
    for s in special:
        chars = chars.replace(s, " {} ".format(s))
    return chars.split()


def parse(expr):
    return read_from_tokens(tokenize(expr))


def read_from_tokens(tokens, level=0):
    if not tokens:
        raise SyntaxError('No input')
    ret = None
    t = tokens.pop(0)
    quote = False
    if t == "'":
        quote = True
        t = tokens.pop(0)
    if t == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens, level=level + 1))
        # Pop off final ')'
        tokens.pop(0)
        if level == 0 and tokens:
            raise SyntaxError('Unexpected data after parse: {}'.format(
                ' '.join(tokens)))
        ret = L
    elif t == ')':
        raise SyntaxError('Unexpected ")"')
    else:
        ret = atom(t)

    if quote:
        ret = ['quote', ret]
    return ret


def l_eval(expr, env):
    if isinstance(expr, Symbol):
        _, val = env.lookup(expr.value)
        return val
    elif not isinstance(expr, list):
        return expr
    elif expr[0] == 'lambda':
        arglist = expr[1]
        body = expr[2]
        return Procedure(arglist, body, env)
    elif expr[0] == 'apply':
        # TODO:
        proc = l_eval(expr[1], env)
        args = [l_eval(arg, env) for arg in expr[2:]]
        return [proc(arg) for arg in args]
    elif expr[0] == 'define':
        sym = expr[1]
        if sym.value in env:
            raise ValueError('{} already defined in environment'.format(sym))
        val = l_eval(expr[2], env)
        env[sym.value] = val
        return sym
    elif expr[0] == 'set':
        sym = l_eval(expr[1], env)
        if not isinstance(sym, Symbol):
            raise TypeError('{} is not a Symbol'.format(sym))
        if sym.value not in env:
            raise ValueError('{} not found in environment'.format(sym))
        val = l_eval(expr[2], env)
        env[sym.value] = val
        return sym
    elif expr[0] == 'if':
        try:
            _, cond, true_expr, false_expr = expr
        except ValueError:
            _, cond, true_expr = expr
            false_expr = 'None'
        return (l_eval(true_expr, env) if l_eval(cond, env)
                else l_eval(false_expr, env))
    elif expr[0] == 'cond':
        # TOOD: probably not compliant
        i = 1
        while i < len(expr):
            cond, result = expr[i]
            if l_eval(cond, env):
                return l_eval(result, env)
            i += 1
        # No conditions matched
        return None
    elif expr[0] == 'and':
        result = True
        for exp in expr[1:]:
            result = l_eval(exp, env)
            if result in [None, False]:
                return None
        return result
    elif expr[0] == 'or':
        result = None
        for exp in expr[1:]:
            result = l_eval(exp, env)
            if result not in [None, False]:
                return result
        return result
    elif expr[0] == 'let':
        let_forms = expr[1]
        body = expr[2] if len(expr) > 2 else None
        new_env = Environment(parent=env)
        for form in let_forms:
            new_env[form[0].value] = l_eval(form[1], env)
        return l_eval(body, new_env)
    elif expr[0] == 'map':
        # TODO: probably non-conforming, can we implement this in lisp?
        proc = l_eval(expr[1], env)
        args_list = [l_eval(arg, env) for arg in expr[2:]]
        ret = [proc(*args) for args in zip(*args_list)]
        return ret
    elif expr[0] == 'seq':
        args = [l_eval(arg, env) for arg in expr[1:]]
        ret = range(*args)
        return ret
    elif expr[0] == 'quote':
        return expr[1]
    else:
        proc = l_eval(expr[0], env)
        args = [l_eval(arg, env) for arg in expr[1:]]
        ret = proc(*args)
        if ret is False:
            # Lisp!
            ret = None
        return ret


if __name__ == '__main__':
    read_loop()


from environments import Environment
