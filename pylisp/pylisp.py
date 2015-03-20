#!/usr/bin/env python

from __future__ import unicode_literals

import readline

from environment import Environment, global_env
from utils import red, green


# TODO: http://pymotw.com/2/readline/
# Use readline for completing function names
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')


class Symbol(object):
    def __init__(self, v):
        self.value = v

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
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(expr):
    return read_from_tokens(tokenize(expr))

def read_from_tokens(tokens):
    if not tokens:
        raise SyntaxError('No input')
    t = tokens.pop(0)
    if t == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        # Pop off final ')'
        tokens.pop(0)
        return L
    elif t == ')':
        raise SyntaxError('Unexpected ")"')
    else:
         return atom(t)

def l_eval(expr, env=global_env):
    if isinstance(expr, Symbol):
        value = expr.value
        return env.lookup(expr.value)
    elif not isinstance(expr, list):
        return expr
    elif expr[0] == 'lambda':
        pass
    elif expr[0] == 'apply':
        # TODO:
        proc = l_eval(expr[1], env)
        args = [l_eval(arg, env) for arg in expr[2:]]
        return [proc(arg) for arg in args]
    else:
        proc = l_eval(expr[0], env)
        args = [l_eval(arg, env) for arg in expr[1:]]
        return proc(*args)


def read_loop():
    try:
        readline.read_history_file('.pylisp_history')
    except IOError:
        pass
    count = 1
    while True:
        try:
            expr = raw_input(red('[{}]'.format(count)) + ' > ')
        except EOFError:
            break
        if not expr:
            continue
        try:
            ret = l_eval(parse(expr), global_env)
        except Exception, e:
            print 'Error: {}'.format(e)
            continue
        print green('[{}]'.format(count)) + ' {}'.format(ret)
        print
        count += 1
    print
    readline.write_history_file('.pylisp_history')


if __name__ == '__main__':
    read_loop()
