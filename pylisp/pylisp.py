#!/usr/bin/env python

from __future__ import unicode_literals

RED = '\x1b[31m{}\x1b[0m'
GREEN = '\x1b[32m{}\x1b[0m'

def red(s):
    return RED.format(s)

def green(s):
    return GREEN.format(s)

def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def l_eval(expr):
    for tok in tokenize(expr):
        print tok

def read_loop():
    count = 1
    while True:
        try:
            expr = raw_input(red('[{}]'.format(count)) + ' > ')
        except EOFError:
            print
            break
        if not expr:
            continue
        ret = l_eval(expr)
        print green('[{}]'.format(count)) + ' {}'.format(ret)
        print
        count += 1


if __name__ == '__main__':
    read_loop()
