#!/usr/bin/env python

from __future__ import unicode_literals

import operator
import readline

# TODO: http://pymotw.com/2/readline/
# Use readline for completing function names
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')


RED = '\x1b[31m{}\x1b[0m'
GREEN = '\x1b[32m{}\x1b[0m'

FUNCTIONS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.div,
    '^': operator.pow,
}

def red(s):
    return RED.format(s)

def green(s):
    return GREEN.format(s)

def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def get_function(func):
    # TODO: support for environments
    return FUNCTIONS.get(func)

def l_eval(expr):
    tokens = tokenize(expr)
    for i, tok in enumerate(tokens):
        if tok == '(':
            func = get_function(tokens[i + 1])
            if func:

                pass
        elif tok == ')':
            pass

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
        ret = l_eval(expr)
        print green('[{}]'.format(count)) + ' {}'.format(ret)
        print
        count += 1
    print
    readline.write_history_file('.pylisp_history')


if __name__ == '__main__':
    read_loop()
