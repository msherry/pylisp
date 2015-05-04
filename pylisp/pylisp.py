#!/usr/bin/env python

from __future__ import unicode_literals

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
        from environments import Environment

        env = Environment(parent=self.parent_env)
        for arg, val in zip(self.arglist, args):
            assert isinstance(arg.value, basestring)
            env[arg.value] = val
        return env.eval(self.body)


if __name__ == '__main__':
    read_loop()
